import csv
import numpy as np

from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class Item:
    name: str
    icon: (str, str)

@dataclass
class Character:
    name: str
    level: int
    items: List
    pos: (int, int) = None    # NOT HERE!!!

@dataclass
class Map:
    name: str
    entry: (int, int)
    biomes: np.ndarray
    terrain: np.ndarray

basepath = Path(__file__).parent / "data"

bgpalette = dict(
    beige='#dad992',
    black='#000',
    blue='#66f',
    brown='#884400',
    cyan='#49e',
    dkblue='#223866',
    dkgreen='#3b542b',
    green='#78a758',
    gold='#665533',
    grey='#444444',
    ltgreen='#aaee88',
    pink='#dd99dd',
    white='#fff'
)

fgpalette = bgpalette

def csv_as_dict(f, expected_columns, id_column, id_mapper):
    reader = csv.reader(f)

    columns = next(reader)
    id_index = columns.index(id_column)

    for ec in expected_columns:
        if ec not in columns:
            raise Exception(f'Required column {ec} not present in CSV database')

    d = {}

    for row in reader:
        id = id_mapper(row[id_index])
        d[id] = dict(zip(columns, row))

    return d

def csv_as_dict_of_mapped(f, map_, id_column):
    reader = csv.reader(f)

    columns = next(reader)
    id_index = columns.index(id_column)

    d = {}

    for row in reader:
        id = row[id_index]
        d[id] = map_(**dict(zip(columns, row)))

    return d

def csv_as_list_of_list(f):
    return [row for row in csv.reader(f)]

def reload_data():
    global biomes, maps, tiletypes

    with open(basepath / "maps.csv", 'rt') as f:
        def map_from_csv(filename, name, entryx, entryy):
            with open(basepath / "maps" / (filename + "_biomes.csv"), 'rt') as f:
                biomes = np.array(csv_as_list_of_list(f), dtype=np.uint8)
            with open(basepath / "maps" / (filename + "_terrain.csv"), 'rt') as f:
                terrain = np.array(csv_as_list_of_list(f), dtype=np.uint8)

            return Map(name, (int(entryx), int(entryy)), biomes, terrain)

        maps = csv_as_dict_of_mapped(f, map_from_csv, 'filename')

    with open(basepath / "biomes.csv", 'rt') as f:
        biomes = csv_as_dict(f, set('id,name,bgcolor,fgcolor'.split(',')), 'id', int)

    with open(basepath / "tiletypes.csv", 'rt') as f:
        tiletypes = csv_as_dict(f, set('id,name,icon,cost'.split(',')), 'id', int)

DEFAULT_MAP = 'hello'

reload_data()
