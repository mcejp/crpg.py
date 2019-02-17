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

# https://lospec.com/palette-list/fleja-master-palette
palette = dict(
    beige='#ffe596',
    black='#000',
    blue='#4c93ad',
    brown='#8a503e',
    cyan='#b8fdff',
    dkblue='#233663',
    dkgreen='#309c63',
    dkgrey='#414859',
    green='#51c43f',
    gold='#fcf960',
    grey='#68717a',
    ltgrey='#90a1a8',
    ltgreen='#b4d645',
    pink='#852d66',
    white='#fff'
)

bgpalette = palette
fgpalette = palette

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

# Input:  array of (rows, columns), stored in odd-Y staggered coordinates
# Output: array of (r, q)
def staggered_to_axial(tiles):
    q_offset = int((tiles.shape[0] + 1) // 2)
    out = np.zeros((q_offset + tiles.shape[1], tiles.shape[0]), dtype=tiles.dtype)

    for row in range(tiles.shape[0]):
        for col in range(tiles.shape[1]):
            q = col - int((row - (row % 2)) // 2)
            r = row
            s = -r-q

            assert q_offset + q >= 0
            out[q_offset + q, r] = tiles[row, col]

    return out

def reload_data():
    global biomes, maps, tiletypes

    with open(basepath / "maps.csv", 'rt') as f:
        def map_from_csv(filename, name, entryx, entryy):
            with open(basepath / "maps" / (filename + "_biomes.csv"), 'rt') as f:
                biomes = np.array(csv_as_list_of_list(f), dtype=np.int8)
            with open(basepath / "maps" / (filename + "_terrain.csv"), 'rt') as f:
                terrain = np.array(csv_as_list_of_list(f), dtype=np.int8)

            # fixme: use proper Tiled format
            biomes[np.equal(biomes, -1)] = 0
            terrain[np.equal(terrain, -1)] = 0

            biomes = staggered_to_axial(biomes)
            terrain = staggered_to_axial(terrain)

            return Map(name, (int(entryx), int(entryy)), biomes, terrain)

        maps = csv_as_dict_of_mapped(f, map_from_csv, 'filename')

    with open(basepath / "biomes.csv", 'rt') as f:
        biomes = csv_as_dict(f, set('id,name,bgcolor,fgcolor'.split(',')), 'id', int)

    with open(basepath / "tiletypes.csv", 'rt') as f:
        tiletypes = csv_as_dict(f, set('id,name,icon,cost'.split(',')), 'id', int)

DEFAULT_MAP = 'hello'

reload_data()
