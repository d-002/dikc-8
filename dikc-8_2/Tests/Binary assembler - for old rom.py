from os import getenv, makedirs
from os.path import splitext, basename, join, exists
from litemapy import Schematic, Region, BlockState

filename = 'scripts/interaction.ass2'
name = splitext(filename)[0]

data = ''
with open(filename) as f:
    i = 0
    for line in f.readlines():
        line = [c for c in line if c in '01']
        if len(line) != 16: raise SyntaxError('Invalid line %d (%s)' %(i, line))
        data += ''.join(line)
        i += 1

schematics_folder = join(getenv('appdata'), '.minecraft\\schematics\\DIKC-8 II ROMs')
if not exists(schematics_folder):
    makedirs(schematics_folder)

reg = Region(0, 0, 0, 31, 15, 50)
name = basename(name)
schem = Schematic(name=name, author='D_00', regions={name: reg}, lm_version=5)
noteblock = BlockState('minecraft:note_block')
rail = BlockState('minecraft:powered_rail')

i = 0
for y in range(8):
    for x in range(16):
        for z in range(16):
            Z = 2*z if z < 6 else 42-2*z if z < 11 else 71-2*z
            block = noteblock if i < len(data) and data[i] == '1' else rail
            reg.setblock(30 - x*2, y*2, Z, block)
            i += 1

path = join(schematics_folder, basename(name)+'.litematic')
schem.save(path)
print('Successfully exported to %s' %path)
