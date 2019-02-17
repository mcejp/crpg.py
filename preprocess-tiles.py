# Preprocess tile images to use desired color
import subprocess
from pathlib import Path

import game
from game import data

studio_data_path = game.package_base_path / 'studio_data'
biomes_png_path = studio_data_path / 'biomes'
tiles_png_path = studio_data_path / 'tiles'

png_size = (56, 64)

tiletype_list = []

for required_path in [biomes_png_path, studio_data_path, tiles_png_path]:
    required_path.mkdir(parents=True, exist_ok=True)

def convert(from_, to, background='transparent', resize=None):
    command = ['convert', '-background', background]

    if resize:
        command += ['-resize', '%dx%d' % resize]

    command += [from_, to]
    subprocess.check_call(command)

def generate_blank_image(path, w, h, color):
    subprocess.check_call(['convert', '-size', f'{w}x{h}', 'canvas:' + color, path])

for id, tiletype in data.tiletypes.items():
    print('preprocess', tiletype['name'])
    # TODO: tiled's CSV format is retarded, we need to work around it / use something else

    src_file = game.package_base_path / 'static' / 'icons' / (tiletype['icon'] + '.svg')
    png32_file = tiles_png_path / (str(id) + '.png')

    #bgcolor = data.bgpalette[tiletype['bgcolor']]
    bgcolor = 'transparent'

    if src_file.is_file():
        with open(src_file, 'rt') as input:
            svg = input.read()

        for biome_id, biome in data.biomes.items():
            if biome['fgcolor'] == '':
                continue

            fgcolor = data.fgpalette[biome['fgcolor']]
            dst_file = game.package_base_path / 'static' / 'icons' / 'tiles' / f"{id}.{biome['fgcolor']}.svg"

            with open(dst_file, 'wt') as output:
                output.write(svg.replace('#fff', fgcolor))

        subprocess.check_call(['convert', '-resize', f'{png_size[0]}x{png_size[1]}', '-background', bgcolor, dst_file, png32_file])
    else:
        # TODO: red-fill explicitly invalidated tile types
        generate_blank_image(png32_file, png_size[0], png_size[1], bgcolor)

    tiletype_list.append((tiletype, png32_file))

##### generate all needed hex backgrounds
print('make hexes')

with open(game.package_base_path / 'static' / 'icons' / 'hex.svg', 'rt') as input:
    svg = input.read()

def generate_hex_by_colorname(colorname):
    bgcolor = data.palette[colorname]
    dst_file = game.package_base_path / 'static' / 'icons' / 'tiles' / f"hex.{colorname}.svg"

    with open(dst_file, 'wt') as output:
        output.write(svg.replace('#fff', bgcolor))

for biome_id, biome in data.biomes.items():
    for colorname in [biome['bgcolor'], biome['fgcolor']]:  # TODO: remove fgcolor from this list when definitely not needed
        if colorname == '':
            continue

        generate_hex_by_colorname(colorname)

generate_hex_by_colorname('black')

#####
print('make biomes.tsx')

with open(studio_data_path / 'biomes.tsx', 'wt') as tsx:
    tsx.write(f'''\
<?xml version="1.0" encoding="UTF-8"?>
<tileset name="biomes" tilewidth="{png_size[0]}" tileheight="{png_size[1]}" tilecount="{len(tiletype_list)}" columns="0">
  <grid orientation="orthogonal" width="1" height="1"/>
''')

    # TODO: somewhere we need to assert that there are no gaps in IDs
    for i, id in enumerate(data.biomes.keys()):
        assert id == i

        biome = data.biomes[id]

        colored_hex_svg = game.package_base_path / 'static' / 'icons' / 'tiles' / f"hex.{biome['bgcolor']}.svg"

        png = biomes_png_path / (str(id) + '.png')
        convert(colored_hex_svg, png, resize=png_size)

        tsx.write(f'''\
  <tile id="{i}" type="{biome['name']}">
    <image width="{png_size[0]}" height="{png_size[1]}" source="{png}"/>
  </tile>
''')

    tsx.write('''\
</tileset>
''')

print('make tileset.tsx')

with open(studio_data_path / 'tileset.tsx', 'wt') as tsx:
    tsx.write(f'''\
<?xml version="1.0" encoding="UTF-8"?>
<tileset name="terrain_tiles" tilewidth="{png_size[0]}" tileheight="{png_size[1]}" tilecount="{len(tiletype_list)}" columns="0">
  <grid orientation="orthogonal" width="1" height="1"/>
''')

    # TODO: somewhere we need to assert that there are no gaps in IDs
    for i, (tiletype, png32_file) in enumerate(tiletype_list):
        tsx.write(f'''\
  <tile id="{i}" type="{tiletype['name']}">
    <image width="{png_size[0]}" height="{png_size[1]}" source="{png32_file}"/>
  </tile>
''')

    tsx.write('''\
</tileset>
''')
