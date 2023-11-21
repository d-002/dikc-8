from files.prompts import *
from files.dikc8export import *

def b(n, size=4):
    b = str(bin(int(n))).split('b')[1]
    return '0'*(size-len(b)) + b

def assemble(filename):
    commands = ['LDI', 'CPI', 'LDB', 'CPB', 'ADD', 'SUB', 'MUL', 'DIV',
                'IFF', 'EQU', 'LES', 'LGC', 'SCR', 'RST', 'END']
    with open(filename) as f:
        lines = f.read().split('\n')

    program = []
    for line in lines:
        if not line: continue
        line = line.split(' ')
        name, args = line[0], line[1:]
        cmd_id = commands.index(name)
        cmd = b(cmd_id)
        if cmd_id in [0, 8]:
            cmd += b(args[0])+b(args[1], 8)
        elif cmd_id in [4, 5, 6, 7, 9, 10]:
            cmd += ''.join(b(a) for a in args)
        elif cmd_id == 1:
            cmd += '0'*4 + b(args[0]) + b(args[1])
        elif cmd_id == 3:
            cmd += b(args[0]) + '0'*4 + b(args[1])
        elif cmd_id == 12:
            cmd += b(args[0]) + b(args[1]) + '0'*4
        elif cmd_id in [13, 14]:
            cmd += '0'*12
        elif cmd_id == 2:
            cmd += b(args[0]) + str(args[1]) + '0'*11
        elif cmd_id == 11:
            if args[0] == 'AND': A, B, C = '100'
            elif args[0] == 'ORR': A, B, C = '010'
            elif args[0] == 'XOR': A, B, C = '001'
            cmd += A+b(args[1], 3)+B+b(args[2], 3)+C+b(args[3], 3)
        if len(cmd) != 16:
            raise SyntaxError()
        program.append(cmd)

    return ''.join(program)

filename, folder = ask_both('ass')
log_init('assembling')

binary = assemble(filename)
export(binary, filename, folder, log, True)
log_wait()
