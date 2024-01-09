# TODO: fix thing with 3 arguments for bit changes
# TODO: add all help

from os import getenv, makedirs
from os.path import splitext, basename, join, exists, isfile
from litemapy import Schematic, Region, BlockState
from sys import argv, stderr

class Fore:
    RED = YELLOW = GREEN = CYAN = RESET = ''

# commands start at index 0, but I added 1000 to avoid conflicts with global bool values
WRT,CPY,BIT,SDB,SCB,DBF,ABF,CBF,EQU,MOR,LES,LSH,RSH,SUB,ADD,NOT,ORR,AND,XOR,JPI,JMP,OUT,OUP,INN,MUL,DIV,MOD,END,NOP,PUS,POP = list(range(1000, 1019))+list(range(1020, 1032))
gl = globals()
# values: 16*(number of arguments) + 4^n * (type of argument n)
commands = {WRT: 1120, CPY: 1096, BIT: 1630, SDB:  512, SCB: 1112, DBF:  512,
            ABF:  512, CBF: 1112, EQU: 1096, MOR: 1096, LES: 1096, LSH:  576,
            RSH:  576, SUB: 1096, ADD: 1096, NOT:  576, ORR: 1096, AND: 1096,
            XOR: 1096, JPI:  832, JMP:  832, OUT: 1104, OUP: 1104, INN: 1104,
            MUL: 1096, DIV: 1096, MOD: 1096, END:    0, NOP:    0, PUS:    0,
            POP:    0}
# instructions that take multiple cycles
multiple = {JPI: 2, JMP: 2, MUL: 2, DIV: 3, MOD: 3}
for i in range(1000, 1033):
    if i != 19 and i not in multiple: multiple[i] = 1
# instructions that can FOR SURE run in parallel
# (others: only show a warning because may still work)
parallel = [WRT, CPY, BIT, SDB, SCB, DBF, JMP, OUT, OUP, INN, END, NOP, PUS, POP]
explanation = {
    WRT: 'Writes 5-bit value to register',
    CPY: 'Copies register a to register b',
    BIT: 'Sets bit of register a at index b (0: least significant) to value c',
    SDB: 'Sets data buffer (used to then store 8-bit values in registers, see DBF)',
    SCB: 'Sets compare buffer to register a\'s bit at index b (0: least significant)',
    DBF: 'Data buffer to register',
    ABF: 'ALU buffer to register',
    CBF: 'Compare buffer to register a at bit of index b (0: least significant)',
    EQU: 'Sets compare buffer to register a == register b',
    MOR: 'Sets compare buffer to register a > register b',
    LES: 'Sets compare buffer to register a < register b',
    LSH: 'Left shift (multiplication by 2) into ALU buffer',
    RSH: 'Right shift (integer division by 2) into ALU buffer',
    SUB: 'Puts a-b into ALU buffer',
    ADD: 'Puts a+b into ALU buffer',
    NOT: 'Bitwise NOT into ALU buffer',
    ORR: 'Bitwise OR into ALU buffer',
    AND: 'Bitwise AND into ALU buffer',
    XOR: 'Bitwise XOR into ALU buffer',
    JPI: 'Jumps to address if the compare buffer is True',
    JMP: 'Jumps to address',
    OUT: 'Writes value to I/O port',
    OUP: 'Pulses (writes number, then writes a 0) to I/O port',
    INN: 'Writes I/O port value into register',
    MUL: 'Puts a*b into ALU buffer',
    DIV: 'Puts a/b (integer division) into ALU buffer',
    MOD: 'Puts a%b into ALU buffer',
    END: 'Stops the program\'s execution',
    NOP: 'Stalls for one cycle',
    PUS: 'Push the current program counter value into the call stack',
    POP: 'Put the latest (default 0) call stack value into the program counter'
}
MAXINT = 256
WORDSIZE = 8 # bits
RAMSIZE = 32 # bytes
ROMSIZE = 128 # instructions
IOSIZE = 8 # bytes
WRTLIMIT = 32
comments = ('Number', 'Address', 'IO address', 'Bit index', 'Short value', 'Program counter address', 'Single bit')
bounds = (MAXINT, RAMSIZE, IOSIZE, WORDSIZE, WRTLIMIT, ROMSIZE, 2)

def _help(cmd):
    name = get_cmd_name(cmd)
    if name is None: raise NotImplementedError('This command does not exist')
    syntax = Fore.CYAN + name + ''.join(' '+chr(97+i) for i in range(commands[cmd]>>9)) + Fore.RESET
    types = []
    for i in range(commands[cmd]>>9):
        j = (commands[cmd] & (7 << 6-3*i)) >> 6-3*i
        if j == 3 and cmd == WRT: j = 4 # special limit for WRT value
        types.append('    | - %s: %s (between 0 and %d)' %(chr(97+i), comments[j], bounds[j]-1))
    cycles = '' if multiple[cmd] == 1 else Fore.YELLOW + '\nTakes %d cycles' %multiple[cmd] + Fore.RESET
    types = '\n'+'\n'.join(types) if types else ' [no arguments]'
    print("""\n%sHelp on command %s (code %d):%s
  %s%s
  Syntax: %s
  Arguments:%s\n""" %(Fore.CYAN, name, cmd-1000, Fore.RESET, explanation[cmd], cycles, syntax, types))

def is_cmd(word):
    return word == '.def' or len(word) == 3 and word.upper() in gl

def get_cmd_name(cmd):
    names = [key for key in gl if gl[key] == cmd]
    if len(names): return names[0]

def atline():
    l = file_lines[line-1]
    return '. At line %d: "%s%s"' %(line, l[:30], '...' if len(l) > 30 else '')

def _bin(n, bits):
    s = ''
    for _ in range(bits):
        s = str(n&1) + s
        n >>= 1
    return s

def correct_var(var):
    """Checks if a variable is correct.
Correct variable means:
  - cannot be a command name
  - only alphanumeric characters and _
  - cannot be only a _
  - at least a character long
  - cannot start with a number"""
    v = var.replace('_', '')
    if not v: return False
    if var.upper() in gl: return False
    if 47 < ord(var[0]) < 58: return False
    return v.isalnum()

def correct_value(value, type):
    """Checks if a value is correct.
Type defines the (excluded) upper bound:
  - 0: MAXINT
  - 1: RAMSIZE
  - 2: IOSIZE
  - 3: WORDSIZE
  - 4: WRTLIMIT
  - 5: ROMSIZE
  - 6: 2
Correct value means:
  - numeric
  - in bounds (not mandatory, warns)"""
    if not value: return False
    if not value.isnumeric(): return False
    if int(value) >= bounds[type] and show_warnings:
        print(Fore.RED + 'WARNING: %s %s is out of bounds (>= %d).' %(comments[type], value, bounds[type]) + atline())
    return True

def export(file):
    global file_lines, line # for atline()

    print('\nExporting', file)
    if show_warnings: print(Fore.RED+"""WARNING: This program will not add NOP for longer instructions,
         to allow for more freedom concerning parallel execution.
         You will be warned in case some incompatible instructions
         are detected, but make sure to add NOP for extra safety.""")
    else: print(Fore.YELLOW+'Warnings are DISABLED')

    print('\nReading file, removing tabs and comments...')
    raw = ''
    with open(file) as f:
        file_lines = f.read().split('\n')
    for l in file_lines:
        raw += l.split(';')[0].replace('\t', '').replace('\r', '')+'\n'
    print(Fore.GREEN+'[Done]')

    print('\nRemoving useless spaces, getting lines/instructions links...')
    code, current, prev = '', '', raw[0].isalnum()
    linebreaks = [] # used to remember raw line index for errors
    for i in range(len(raw)+1):
        if i == len(raw): now = not prev
        else: now = raw[i].isalnum() or raw[i] == '_'
        if now != prev:
            if now:
                if current == '.': current = ' '+current
                else: current += ' '
                code += current
            else: code += current
            current = ''
        if i == len(raw): continue
        if now: current += raw[i]
        elif raw[i] not in ' ,=\n': current += raw[i]
        if raw[i] == '\n': linebreaks.append(len(code)+1)
        prev = now
    print(Fore.GREEN+'[Done]')

    print('\nSplitting into instructions...')
    vars = {} # defined variables
    points = {} # defined jump points
    program = []
    program_lines = [] # raw lines corresponding to instructions
    current = None # (cmd, [args]), or (for .def): ('.def', name)
    remaining = 0 # remaining arguments for this instruction
    i = 0
    end = False
    for word in code.split(' '):
        i += len(word)+1
        line = 1
        for l in linebreaks:
            if l < i: line += 1
            else: break
        if word == '': continue # can happen with a .def at the start
        if remaining == 0: # new instruction
            if word == '.def': # define variable
                current = [word, None]
                remaining = 2
            elif word[-1] == ':': # jump point
                if not correct_var(word[:-1]):
                    raise ValueError(Fore.RED+'Incorrect jump point name'+atline())
                points[word[:-1]] = len(program)
            else:
                if not is_cmd(word):
                    raise NotImplementedError(Fore.RED+'Unknown command: '+word+atline())
                cmd = gl[word.upper()]
                if cmd == END: end = True
                current = [cmd, []]
                remaining = commands[cmd]>>9
                if not remaining: # command with no arguments
                    program.append(current)
                    program_lines.append(line)
        else: # new argument
            if current[0] == '.def':
                if remaining == 2:
                    if not correct_var(word):
                        raise ValueError(Fore.RED+'Incorrect variable name: '+word+atline())
                    current[1] = word
                elif remaining == 1:
                    if not correct_value(word, 0):
                        raise ValueError(Fore.RED+'Incorrect value: '+word+atline())
                    vars[current[1]] = int(word)
            elif is_cmd(word):
                name = get_cmd_name(current[0])
                raise AttributeError(Fore.RED+'Not enough arguments for "%s": expected %d, got %d%s' %(name, commands[current[0]]>>9, len(current[1]), atline()))
            else:
                # no value check, wait till all variables are loaded
                current[1].append(word)
                if remaining == 1: # end of instruction: add it to program
                    program.append(current)
                    program_lines.append(line)
            remaining -= 1
    print(Fore.GREEN+'[Done]')
    if remaining: raise EOFError(Fore.RED+'Unexpected end of file.')
    if len(program) > ROMSIZE:
        raise MemoryError(Fore.RED+'Out of program memory (%d/%d).' %(len(program), ROMSIZE))
    if not end and show_warnings:
        print(Fore.RED+'WARNING: No END instruction detected.')
    print('%d variables, %d jump points' %(len(list(vars.keys())), len(list(points.keys()))))

    print('\nHandling variables...')
    i = 0
    for cmd, args in program:
        line = program_lines[i]
        i += 1
        for j in range(len(args)):
            a = args[j]
            if cmd in (JPI, JMP):
                if a in points:
                    error = 0
                    args[j] = points[a]
                else: error = 1
            elif a in vars:
                error = 0
                args[j] = vars[a]
            else:
                t = (commands[cmd] & (7 << 6-3*j)) >> 6-3*j
                if t == 3 and cmd == WRT: t = 4
                if correct_value(a, t):
                    error = 0
                    args[j] = int(a)
                else: error = 2
            if error:
                e = 'Incorrect program pointer' if error == 1 else 'Unknown value'
                raise ValueError(Fore.RED + '%s: "%s".' %(e, a) + atline())
    print(Fore.GREEN+'[Done]')

    print('\nChecking parallel code execution...')
    running = [] # [cmd, remaining cycles]
    for i in range(len(program)):
        cmd = program[i][0]
        line = program_lines[i]
        done = []
        for r in running:
            r[1] -= 1
            if r[1] == 0: done.append(r)
            else:
                a, b = get_cmd_name(r[0]), get_cmd_name(cmd)
                if cmd in parallel:
                    if cmd != NOP:
                        print('  | %sNoticed overlap between %s and %s at line %d' %(Fore.CYAN, a, b, line))
                elif show_warnings:
                    print('%sWARNING: Possible conflict between instructions %s (%d cycles remaining) and %s%s' %(Fore.YELLOW, a, r[1], b, atline()))
        for d in done: running.remove(d)
        running.append([cmd, multiple[cmd]])
    print(Fore.GREEN+'[Done]')

    print('\nFormatting into machine code...')
    # add 0s for 0 and 1 argument instructions, split into 5-bit arguments
    data = ''
    i = 0
    for p in program:
        cmd, args = p
        if cmd in (DBF, ABF): p[1] = [args[0], 0]
        elif cmd in (LSH, RSH, NOT): p[1] = [0, args[0]]
        elif cmd in (JPI, JMP): p[1] = [args[0]>>5<<2, args[0]&31]
        elif cmd in (DIV, MOD): p[1] = [args[1], args[0]]
        elif cmd == BIT: p[1] = [args[0], (args[1]*2 & 14) + (args[2]&1)]
        elif cmd == CBF: p[1] = [args[0], args[1]*2 & 14]
        elif cmd == SDB: p[1] = [args[0]>>3, (args[0]&7)<<2]
        elif not args: p[1] = [0, 0]
        if show_code: print('%s %s %s' %(get_cmd_name(cmd), _bin(p[1][0], 5), _bin(p[1][1], 5)), i)
        i += 1
        data += _bin(cmd-1000, 6)+_bin(p[1][0], 5)+_bin(p[1][1], 5)
    print(Fore.GREEN+'[Done]')

    print('\nExporting to schematic...')
    schematics_folder = join(minecraft_folder, 'schematics/DIKC-8 II ROMs')
    if not exists(schematics_folder):
        makedirs(schematics_folder)
        print('  | Created folder', schematics_folder)

    reg = Region(0, 0, 0, 33, 16, 53)
    filename = splitext(basename(file))[0]
    schem = Schematic(name=filename, author='D_00', regions={filename: reg}, lm_version=5)
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

    path = join(schematics_folder, filename+'.litematic')
    schem.save(path)
    print(Fore.GREEN + '[Done]%s\nSuccessfully exported to %s' %(Fore.RESET, path))

    used = round(len(program)/ROMSIZE*100)
    print('\nProgram takes %d instructions' %len(program))
    print('ROM used: %d/%d bytes (%d%%), %d%% free' %(len(program)<<1, ROMSIZE<<1, used, 100-used))
    print(Fore.CYAN+'Make sure to paste with non-air with Litematica.')

# read options from file
minecraft_folder = join(getenv('appdata'), '.minecraft')
show_warnings, show_code, colors = True, False, True
if exists('options.txt'):
    with open('options.txt') as f:
        try:
            for i, line in enumerate(f.read().split('\n')):
                if i == 0: minecraft_folder = line
                elif i == 1: show_warnings = int(line)
                elif i == 2: show_code = int(line)
                elif i == 3: colors = int(line)
                else: break
        except: print('Error loading options')
else: print('Created options file')

def save_options():
    with open('options.txt', 'w') as f:
        f.write('\n'.join((minecraft_folder, '%d' %show_warnings, '%d' %show_code, '%d' %colors)))
def initcolors():
    global Fore, is_init
    if colors:
        try:
            from colorama import init, Fore
        except:
            raise ImportError('colorama failed to load. Consider downloading it or using -c')
        is_init = True
        init(autoreset=True)
save_options()
is_init = False

if False: # enable this while debugging
    colors = False
    show_code = True
    argv = []
    for i in range(1000, 1032):
        if i != 1019:
            _help(i)
    export('scripts/addtest.ass2')

# get command line arguments
argv.pop(0)
if not len(argv): # no arguments: display help
    print("""%sass2 to schematic
\nUsage:%s
    - ass2schem [-f] filename [-w value] [-p value] [-c value]
    - ass2schem -h command
    - ass2schem -d -m/-w/-p/-c value
%sArguments:%s
    No args        Display help.
    [-f] file      Export "file" to schematic (e.g. py ass2schem myfile.ass2)
    -h command     Display instruction help (e.g. py ass2schem -h WRT)
    -d arg value   Set default value for argument to value (value: 0/1)
    -m path        Path to minecraft .minecraft folder
    -w value       Display warnings
    -p value       Display program code
    -c value       Use colors""" %(Fore.CYAN, Fore.RESET, Fore.CYAN, Fore.RESET))
else:
    code = 0
    if argv[0] == '-f': argv.pop(0)
    if len(argv):
        if argv[0] == '-h':
            initcolors()
            if len(argv) == 2:
                cmd = argv[1].upper().strip()
                if cmd in gl: _help(gl[cmd])
                else: _help(-1)
            else: code = 1
        elif argv[0] == '-d':
            if len(argv) == 3:
                if argv[1] == '-m': minecraft_folder = argv[2]
                elif argv[1] == '-w': show_warnings = int(argv[2])
                elif argv[1] == '-p': show_code = int(argv[2])
                elif argv[1] == '-c': colors = int(argv[2])
                else: code = 2
            else: code = 3
            if not code: print('Success')
            save_options()
        else:
            if not exists(argv[0]) and isfile(argv[0]): raise FileNotFoundError(Fore.RED+'file '+argv[0]+' does not exist.')
            current = -1
            for i in range(1, len(argv)): # set temporary options
                if i&1: # get option to set
                    if argv[i] not in ('-m', '-w', '-p', '-c'):
                        code = 4
                        break
                    current = ('-m', '-w', '-p', '-c').index(argv[i])
                else: # set option
                    if current == 0: minecraft_folder = argv[i]
                    elif current == 1: show_warnings = int(argv[i])
                    elif current == 2: show_code = int(argv[i])
                    elif current == 3:
                        colors = int(argv[i])
                        initcolors()
                    current = -1
            if current != -1: code = 5
            if not code:
                if not is_init: initcolors()
                export(argv[0])
    else: code = 6
    if code: raise SyntaxError('The syntax of the command is incorrect. Error code: %d' %code)
