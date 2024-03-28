from os import getenv, makedirs
from os.path import splitext, basename, join, exists
from litemapy import Schematic, Region, BlockState

filename = 'scripts/interaction.raw'
name = splitext(filename)[0]

data = ''
with open(filename) as f:
    i = 0
    for line in f.readlines():
        line = ''.join(c for c in line if c in '01')
        if len(line) != 16: raise SyntaxError('Invalid line %d (%s)' %(i, line))
        data += line
        i += 1

schematics_folder = join(getenv('appdata'), '.minecraft\\schematics\\DIKC-8 II ROMs')
if not exists(schematics_folder):
    makedirs(schematics_folder)

reg = Region(0, 0, 0, 33, 16, 53)
name = basename(name)
schem = Schematic(name=name, author='D_00', regions={name: reg}, lm_version=5)
blocks = [BlockState('minecraft:lime_wool'),
          BlockState('minecraft:redstone_wire')]

i = 0
for y in range(8):
    for x in range(16):
        for z in range(16):
            j = 0 if i >= len(data) else data[i] == '1'
            add = 0 if z < 6 else 45 if z < 11 else 74
            mul = 2 if z < 6 else -2
            reg.setblock(31 - x*2, y*2, add + z*mul, blocks[j])
            i += 1

path = join(schematics_folder, basename(name)+'.litematic')
schem.save(path)
print('Successfully exported to %s' %path)
