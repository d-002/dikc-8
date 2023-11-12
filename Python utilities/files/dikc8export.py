from os import getenv, makedirs, name
from os.path import splitext, basename, join, exists
from litemapy import Schematic, Region, BlockState

def export(data, filename, override_ass=False):
    name = splitext(filename)[0]

    # exporting as assembly (.ass)
    if not override_ass:
        commands = ['LDI', 'CPI', 'LDB', 'CPB', 'ADD', 'SUB', 'MUL', 'DIV',
                    'IFF', 'EQU', 'LES', 'LGC', 'SCR', 'RST', 'END']
        lines = []
        for x in range(len(data)//16):
            line = [int(data[x*16 + y*4:x*16 + y*4 + 4], 2) for y in range(4)]
            cmd_id, args = line[0], line[1:]
            cmd = commands[cmd_id]+' '
            if cmd_id in [0, 8]:
                cmd += '%d %d' %(args[0], args[1]*16 + args[2])
            elif cmd_id in [4, 5, 6, 7, 9, 10]:
                cmd += ' '.join(str(a) for a in args)
            elif cmd_id in [1, 3]:
                cmd += ' '.join(str(a) for a in args[1:])
            elif cmd_id == 12:
                cmd += ' '.join(str(a) for a in args[:2])
            elif cmd_id in [13, 14]:
                cmd = cmd[:-1]
            elif cmd_id == 2:
                cmd += '%d %d' %(args[0], args[1]/8)
            elif cmd_id == 11:
                if args[0]//8: cmd += 'AND '
                elif args[1]//8: cmd += 'ORR '
                elif args[2]//8: cmd += 'XOR '
                cmd += ' '.join(str(a%8) for a in args)
            lines.append(cmd)

        with open(name+'.ass', 'w') as f:
            f.write('\n'.join(lines))
        print('Successfully exported to %s.ass' %name)

    # exporting as binary (.bin)
    array = bytearray(int(data[i:i+8], 2) for i in range(0, len(data), 8))
    with open(name+'.bin', 'wb') as f:
        f.write(array)
    print('Successfully exported to %s.bin' %name)

    # exporting as schematic (.litematic)
    reg = Region(0, 0, 0, 31, 15, 32)
    schem = Schematic(name=basename(name), author='D_00', regions={name: reg}, lm_version=5)
    noteblock = BlockState('minecraft:note_block')
    rail = BlockState('minecraft:powered_rail')

    index = 0
    for y in range(8):
        for x in range(16):
            for z in range(16):
                z *= 2
                if z > 15:
                    z += 1
                if index < len(data) and data[index] == '1':
                    reg.setblock(30 - 2*x, 2*y, z, noteblock)
                else:
                    reg.setblock(30 - 2*x, 2*y, z, rail)
                index += 1

    path = join(schematics_folder, basename(name)+'.litematic')
    schem.save(path)
    print('Successfully exported to %s' %path)

if name=='nt':
    schematics_folder = join(getenv('appdata'), '.minecraft\\schematics\\DIKC-8 ROMs')
else:
    schematics_folder = 'Export Scripts'
if not exists(schematics_folder):
    if not exists('Export Scripts'):
        makedirs('Export Scripts')
    schematics_folder = 'Export Scripts'
