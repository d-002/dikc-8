from files.prompts import *
from files.dikc8export import *

class CMD:
    def __init__(self, type_, args):
        self.type = type_
        self.args = args

        # [next instruction, where to go if condition true (only for IF)]
        self.goto = [None, None]
        self.forced = False # used by IFs

    def __repr__(self):
        return '%s %s' %(self.type, self.args)
        goto = '|'.join([str(program.index(g)) if g else '' for g in self.goto])
        return '%s %d -> %s' %(self.type,
                               program.index(self),
                               goto)

    def redirect_links(self, program):
        # when deleting, some IFs can still be redirecting to it
        for cmd in program:
            if self == cmd.goto[0]:
                # self is following another command
                cmd.goto[0] = self.goto[0]
            if self == cmd.goto[1]:
                # self is IF success
                cmd.goto[1] = self.goto[0]

def temp_var(type_):
    global temp_count
    name = 'temp.%d' %temp_count
    all_vars[name] = type_
    temp_count += 1
    return name

def get_raw(filename):
    with open(filename) as f:
        raw = 'START;'+f.read().strip()+'END;'
    log('Successfully opened %s' %filename)

    # remove single_line comments, remove line breaks
    lines, raw = raw.split('\n'), ''
    for line in lines:
        if '//' in line:
            raw += line[:line.index('//')]
        else:
            raw += line
    # remove tabs
    raw = raw.replace('\t', '')

    # delete duplicate spaces
    while raw.count('  '):
        raw = raw.replace('  ', ' ')
    # delete leading spaces
    raw = raw.replace('{ ', '{')
    raw = raw.replace('; ', ';')

    # remove comments
    while '/*' in raw:
        start = raw.index('/*')
        end = raw[start:].index('*/')
        raw = raw[:start] + raw[start+end+2:]

    return raw

def split(string):
    # split in alphanumeric and non-alphanumeric strings
    words = []
    last_type = -1
    for char in string.strip():
        if char.isalnum():
            type_ = 0
        else:
            type_ = 1
        if type_ == last_type:
            words[-1] += char
        else:
            words.append(char)
        last_type = type_
    return [w.strip() for w in words]

def get_brackets(string, brackets):
    deep = 0
    start = end = None

    for i in range(len(string)):
        char = string[i]
        if char == brackets[0]:
            if not deep and start is None:
                start = i
            deep += 1
        elif char == brackets[1]:
            deep -= 1
            if not deep and end is None:
                end = i

    if start is None:
        raise SyntaxError('Missing '+brackets[0])
    if end is None:
        raise SyntaxError('Missing '+brackets[1])
    return start, end

def mkvar(program, var, type_):
    # make sure string is a variable (if it's a number, create a temp var)
    if var.isnumeric():
        name = temp_var(type_)
        program.append(CMD(type_, [name, var]))
        return name
    elif var not in all_vars:
        raise NameError(var+' is not defined')
    return var

def check_value(value):
    # "format" value and check if defined
    if value == 'undefined':
        return '256'
    if not value.isnumeric() and value not in all_vars:
        raise NameError(value+' is not defined')
    return value

def calc(program, var, words, new, can_edit=False):
    if len(words) == 1: # no operations, just setting var
        value = check_value(words[0])
        if new:
            # initializing var
            program.append(CMD(all_vars[var], [var, value]))
        else:
            # setting existing var to another var or a number
            program.append(CMD('SET'+all_vars[var], [var, value]))
        return

    type_ = all_vars[var]
    if type_ == 'INT':
        operators = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
    else:
        operators = {'&': 'AND', '|': 'ORR', '^': 'XOR'}

    if new:
        # if var hasn't been defined yed, make it be 256 (<==> undefined):
        # needed for only reserving a memory slot
        program.append(CMD(type_, [var, '256']))

    temp = None
    a = mkvar(program, words[0], type_) # thing to take as "a" in operations
    for i in range(1, len(words), 2):
        b = mkvar(program, words[i+1], type_)

        if can_edit or i == len(words)-2:
            c = var
        else: # keep the value of var during calculations, create a temp one instead
            if temp is None:
                temp = temp_var(type_)
                program.append(CMD(type_, [temp, '256']))
            c = temp
        program.append(CMD(operators[words[i]], [a, b, c]))
        a = c

def get_condition(program, raw):
    start, end = get_brackets(raw, '()')
    words = split(raw[start+1:end])
    comparison = False
    for o in '=<>':
        if o in raw:
            comparison = True

    # define a temp variable containing condition result if needed
    if comparison or len(words) > 1:
        dst = temp_var('BOOL')
        program.append(CMD('BOOL', [dst, '256']))
    else: # no calculation at all, just one variable name
        return words[0], False

    if comparison: # condition is a comparison
        # find the index of the comparison characters
        for i in range(len(words)):
            w = words[i]
            if '=' in w or '<' in w or '>' in w:
                index = i
                break

        # for each side of the comparison, get its variable name
        # or create a new variable if it's a calculation
        if index == 1:
            a = mkvar(program, words[0], 'INT')
        else:
            a = temp_var('INT')
            calc(program, a, words[:index], True, True)
        if index == len(words)-2:
            b = mkvar(program, words[-1], 'INT')

        else:
            b = temp_var('INT')
            calc(program, b, words[index+1:], True, True)

        # rearrange a and b, invert if needed, to only use EQ and LT
        invert = False
        if words[index] == '==':
            program.append(CMD('EQ', [a, b, dst]))
        elif words[index] == '<':
            program.append(CMD('LT', [a, b, dst]))
        elif words[index] == '>':
            program.append(CMD('LT', [b, a, dst]))
        elif words[index] == '<=':
            program.append(CMD('LT', [b, a, dst]))
            invert = True
        elif words[index] == '>=':
            program.append(CMD('LT', [a, b, dst]))
            invert = True
        return dst, invert

    else: # condition is a calculation of bools
        calc(program, dst, words, False, True)
        return dst, False

def get_cmd(raw):
    program = []
    to_define, next_to_define = [], []

    while len(raw):
        newline = raw.index(';')+1
        cmd_raw = ''
        for char in raw:
            if not char.isalpha():
                break
            cmd_raw += char
        cmd = cmd_raw.upper()

        line_err = 'in instruction "%s": ' %raw[:newline-1]

        if cmd_raw in all_vars: # var = value;
            words = split(raw[:newline-1])

            if words[0] not in all_vars:
                raise NameError(line_err+words[0]+' is not defined')

            calc(program, words[0], words[2:], False)
            raw = raw[newline:]

        elif cmd in TYPES: # int/bool var value;
            words = split(raw[len(cmd):newline-1])

            # store variable and its type
            all_vars[words[0]] = cmd

            calc(program, words[0], words[2:], True)
            raw = raw[newline:]

        elif cmd in ['WHILE', 'IF']: # while/if condition { do this }
            # get indices of { and }
            start, end = get_brackets(raw, '{}')

            if cmd == 'WHILE':
                # check the conditions again after WHILE (go to before getting condition)
                index = len(program)

            var, invert = get_condition(program, raw[len(cmd):start])
            program_, to_define_ = get_cmd(raw[start+1:end])
            program.append(CMD('IF', [var, invert, program_, None, cmd]))

            # define an eventual to_define
            for ab in to_define_:
                if ab[1] < len(program_):
                    ab[0].args.append(program_[ab[1]])
                else:
                    if cmd == 'WHILE': # IF at the end of WHILE, link to WHILE start
                        ab[0].args[3] = program[index]
                    else:
                        next_to_define.append([ab[0], len(program)])

            if cmd == 'WHILE':
                program[-1].args[3] = program[index]
            else:
                # go to fail of IF after success (go back to just after the IF command)
                # but will need to define this next time
                next_to_define.append([program[-1], len(program)])

            raw = raw[end+1:]

        elif cmd in ['START', 'END']:
            program.append(CMD(cmd, []))
            raw = raw[newline:]

        elif cmd == 'LIGHTPIXEL':
            start, end = get_brackets(raw[:newline-1], '()')
            args = raw[start+1:end].split(',')
            if len(args) != 2:
                raise TypeError(line_err+'Expected 2 arguments for lightPixel, got %s' %len(args))
            for x in range(2):
                words = split(args[x])
                if len(words) == 1: # just using a variable
                    args[x] = mkvar(program, check_value(words[0]), 'INT')
                else: # calculating something
                    args[x] = temp_var('INT')
                    calc(program, args[x], words, True)

            program.append(CMD('SCR', args))

            raw = raw[newline:]

        elif cmd == 'RESETSCREEN':
            program.append(CMD('RST', []))
            raw = raw[newline:]

        else:
            raise NotImplementedError(line_err+cmd+' command not recognised')

        # if previous command was an IF, clearly define its go_back_to
        for ab in to_define:
            ab[0].args[3] = program[ab[1]]
        to_define, next_to_define = next_to_define, []

    for x in range(len(program)-1):
        # set goto[0] of each command to next command
        program[x].goto[0] = program[x+1]

    return program, to_define

def use_goto(program):
    # also "flattens" program: no list of lists
    ok = False
    while not ok:
        ok = True
        for cmd in program:
            if cmd.type == 'IF' and cmd.goto[1] is None: # found an incorrect IF
                # IF's previous args: [condition var, invert, where to go if success]
                invert = cmd.args[1]
                success = cmd.args[2]
                go_back_to = cmd.args[3]
                true_type = cmd.args[4]
                cmd.args = [cmd.args[0]]

                # set IF's success goto to the first command of success
                cmd.goto[invert] = cmd.goto[0]
                cmd.goto[1-invert] = success[0]

                end = success[0]
                while end.goto[0] is not None:
                    end = end.goto[0]
                cmd.success_end = end # save this for when deleting CMDs

                # link end of success to go_back_to with a forced IF command
                # (don't need this for inverted IFs)
                if not invert or true_type == 'WHILE':
                    if_ = CMD('IF', [None])
                    if_.forced = True
                    if_.goto = [None, go_back_to]
                    if_.success_end = end
                    end.goto[0] = if_
                    success.append(if_)

                # add success to the main program
                if invert:
                    # add success right after cmd, because will be run if the condition is not true
                    index = program.index(cmd)
                    program = program[:index+1]+success+program[index+1:]

                    # then, no need for a forced IF because the following commands are when the condition is true
                else:
                    # append success at the end, not interfering, because will have a goto into it and at the end
                    program.extend(success)

                ok = False
                break

    log('%d instructions decoded (max %d)' %(len(program), rom_size))
    return program

def use_slots(program):
    def get_temp_info(ignore):
        # get when each var is used
        ranges = {type_: {} for type_ in TYPES}
        for i in range(len(program)):
            if program[i].forced:
                continue
            for arg in program[i].args:
                if '.' in arg and arg not in ignore:
                    type_ = all_vars[arg]
                    if arg in ranges[type_]:
                        ranges[type_][arg][1] = i
                    else:
                        ranges[type_][arg] = [i]*2

        # get max number of vars needed at the same time
        max_temp = {type_: 0 for type_ in TYPES}
        for type_ in TYPES:
            for i in range(len(program)):
                count = 0
                for var, ab in ranges[type_].items():
                    if ab[0] <= i <= ab[1]:
                        count += 1
                if count > max_temp[type_]:
                    max_temp[type_] = count

        # distribute temp vars into slots
        vars_slots = {type_: {} for type_ in TYPES}
        for i in range(len(program)):
            for type_ in TYPES:
                free = list(range(-max_temp[type_], 0))
                for var, ab in ranges[type_].items():
                    if ab[0] <= i <= ab[1]:
                        if var not in vars_slots[type_]:
                            vars_slots[type_][var] = free[0]
                        free.remove(vars_slots[type_][var])

        return vars_slots, max_temp

    # log and check the number of variables
    for type_ in ('INT', 'BOOL'):
        log('Found %d %s variables' %(list(all_vars.values()).count(type_), type_))
    _, max_temp = get_temp_info([])
    for type_ in TYPES:
        log('Peak of %s temp variables: %d' %(type_, max_temp[type_]))
    log('Optimising...')

    # Separate variables into variables and constants
    vars_, constants = [{'INT': [], 'BOOL': []} for _ in range(2)]
    for var, type_ in all_vars.items():
        vars_[type_].append(var)
        constants[type_].append(var)

    # check if variables are modified: remove them from constants
    for cmd in program:
        dst = None # dst will be set to a var if this var is not a constant
        if cmd.type in ['SETINT', 'SETBOOL', 'ADD', 'SUB', 'MUL', 'DIV', 'EQ', 'LT', 'AND', 'ORR', 'XOR']:
            if cmd.type in ['SETINT', 'SETBOOL']:
                dst = cmd.args[0] # this variable is modified
            else:
                dst = cmd.args[2]
        elif cmd.type in TYPES and not cmd.args[1].isnumeric():
            dst = cmd.args[0] # this can be a constant, but its value isn't explicit

        if dst is not None: # remove from constants
            type_ = all_vars[dst]
            if dst in constants[type_]:
                constants[type_].remove(dst)
    # remove constants from vars_
    for type_ in TYPES:
        for const in constants[type_]:
            vars_[type_].remove(const)

    # get the constants that share the same values (duplicates)
    dupe_by_values = {'INT': {}, 'BOOL': {}} # value: [constants using it]
    to_use = {'INT': {}, 'BOOL': {}} # value: constant name to replace to
    for cmd in program:
        if cmd.type in TYPES and cmd.args[0] in constants[cmd.type] and cmd.args[1] != '256':
            var, value = cmd.args
            if value in dupe_by_values[cmd.type]:
                if '.' in var: # temp value: ok to set it as dupe
                    dupe_by_values[cmd.type][value].append(var)
                else: # normal value: set it as reference (in case this constant value doesn't get saved)
                    dupe_by_values[cmd.type][value].append(to_use[cmd.type][value])
                    to_use[cmd.type][value] = var
            else: # new value
                dupe_by_values[cmd.type][value] = []
                to_use[cmd.type][value] = var

    # ram slots usage: first bits for normal vars, last max_temp bits for temp, rest for constants
    for_const = {type_: ram_size[type_]-len([var for var in vars_[type_] if '.' not in var])-max_temp[type_] for type_ in ram_size}
    for type_, n in for_const.items():
        if n < 0:
            raise MemoryError('Out of %s memory (no space for constants)' %type_)

    # choose constants that will have their duplicates removed
    for type_ in TYPES:
        # prefer most used constants, starting with normal constants
        best = sorted(to_use[type_], key=lambda value: len(dupe_by_values[type_][value]), reverse=True)
        best = [to_use[type_][value] for value in best]
        best, not_saved = best[:for_const[type_]], best[for_const[type_]:]

        # check if normal constants are left behind
        for var in not_saved:
            if '.' not in var:
                raise MemoryError('Out of %s memory (to save constants)' %type_)

        # update dupe_by_values and to_use
        to_remove = []
        for value, var in to_use[type_].items():
            if var in not_saved:
                to_remove.append(value)
        for value in to_remove:
            del dupe_by_values[type_][value]
            del to_use[type_][value]

    # remove duplicates that can be edited to a saved variable
    cmd_to_remove = []
    for cmd in program:
        if cmd.forced:
            continue

        # delete instructions that define duplicates
        if cmd.type in TYPES:
            var, value = cmd.args
            if value in dupe_by_values[cmd.type] and var in dupe_by_values[cmd.type][value]:
                cmd_to_remove.append(cmd)
                continue

        # change the var in the instructions that use duplicates
        for i in range(len(cmd.args)):
            if not cmd.args[i].isnumeric():
                type_ = all_vars[cmd.args[i]]
                value = None
                for v, names in dupe_by_values[type_].items():
                    if cmd.args[i] in names:
                        value = v
                        break
                if value is not None:
                    cmd.args[i] = to_use[type_][value]
    for cmd in cmd_to_remove:
        cmd.redirect_links(program)
        program.remove(cmd)

    # remove duplicates from constants
    for type_ in TYPES:
        for names in dupe_by_values[type_].values():
            for dupe in names:
                constants[all_vars[dupe]].remove(dupe)
    replaced_into = [] # constants names to which all constants have been renamed to
    for type_ in TYPES:
        replaced_into.extend(list(to_use[type_].values()))
    temp_slots, max_temp = get_temp_info(replaced_into)
    for type_ in TYPES:
        log('Peak of temp %s variables: %d' %(type_, max_temp[type_]))

    for type_ in TYPES:
        n = len([var for var in vars_[type_] if '.' not in var]+constants[type_])
        log('Reduced to %d %s variables' %(n, type_))
        if n > ram_size[type_]-max_temp[type_]:
            raise MemoryError('Out of %s memory' %type_)

    slots = {type_: [[] for _ in range(ram_size[type_])] for type_ in TYPES}
    index = {type_: [0, len([var for var in vars_[type_] if '.' not in var])] for type_ in TYPES} # [vars, constants] index
    for type_ in TYPES:
        for var in vars_[type_]:
            # map normal variables to slots
            if '.' not in var:
                slots[type_][index[type_][0]].append(var)
                index[type_][0] += 1

            # map temp variables using temp_slots
            else:
                slots[type_][temp_slots[type_][var]].append(var)

        # map constants to constants-reserved slots
        for const in constants[type_]:
            slots[type_][index[type_][1]].append(const)
            index[type_][1] += 1

    # - map CMD var names into their slot
    # - transform e.g. "INT a b" into "SETINT a b" (because a will have been mapped)
    # - transform e.g. "SETINT a 10" into "INT a 10" (doesn't create a duplicate, but works)
    for cmd in program:
        if cmd.forced:
            continue

        if cmd.type in TYPES and not cmd.args[1].isnumeric():
            cmd.type = 'SET'+cmd.type
        elif cmd.type.startswith('SET') and cmd.args[1].isnumeric():
            cmd.type = cmd.type[3:]
        for i in range(len(cmd.args)):
            var = cmd.args[i]
            if not var.isnumeric():
                type_ = all_vars[var]
                for x in range(ram_size[type_]):
                    if var in slots[type_][x]:
                        cmd.args[i] = x

    # define all constants at the start:
    # - get all values assigned to constants-reserved slots
    constants_dict = {type_: {} for type_ in TYPES} # const slot: value
    to_remove = []
    for cmd in program:
        if cmd.type in TYPES and index[cmd.type][0] <= cmd.args[0] < index[cmd.type][1]:
            constants_dict[cmd.type][cmd.args[0]] = cmd.args[1]
            to_remove.append(cmd)

    # - remove all instructions defining constants
    for cmd in to_remove:
        cmd.redirect_links(program)
        program.remove(cmd)

    # - define constants at the start
    for type_ in TYPES:
        for slot, value in constants_dict[type_].items():
            program.insert(0, CMD(type_, [slot, value]))
            program[0].goto[0] = program[1]
    log('Finished handling constants')

def assemble(program):
    def b(n, size=4):
        b = str(bin(int(n))).split('b')[1]
        return '0'*(size-len(b)) + b

    commands = ['INT', 'SETINT', 'BOOL', 'SETBOOL', 'ADD', 'SUB', 'MUL', 'DIV',
                'IF', 'EQ', 'LT', 'logic', 'SCR', 'RST', 'END']

    # remove unneccesary commands
    to_remove = []
    for cmd in program:
        # only needed for reserving a slot
        if cmd.type in TYPES and cmd.args[1] == '256':
            to_remove.append(cmd)
        # START isn't needed
        elif cmd.type == 'START':
            to_remove.append(cmd)
    for cmd in to_remove:
        cmd.redirect_links(program)
        program.remove(cmd)

    # check number of instructions
    log('Reduced to %d instructions (max %d)' %(len(program), rom_size))
    if len(program) > rom_size:
        raise MemoryError('Out of ROM space.')

    # convert all commands to machine language
    binary = []
    for i in range(len(program)):
        cmd, args, goto = program[i].type, program[i].args, program[i].goto
        if cmd in ['AND', 'ORR', 'XOR']:
            id_ = commands.index('logic') # all in 1 command
        else:
            for j in range(len(commands)):
                if cmd == commands[j]:
                    id_ = j
                    break

        current = b(id_)
        if id_ == 0:    current += b(args[0])+b(args[1], 8) # INT
        elif id_ == 1:  current += '0'*4+b(args[1])+b(args[0]) # SETINT
        elif id_ == 2:  current += b(args[0])+str(args[1])+'0'*7 # BOOL
        elif id_ == 3:  current += b(args[1])+'0'*4+b(args[0]) # SETBOOL
        elif id_ == 4:  current += b(args[0])+b(args[1])+b(args[2]) # ADD
        elif id_ == 5:  current += b(args[0])+b(args[1])+b(args[2]) # SUB
        elif id_ == 6:  current += b(args[0])+b(args[1])+b(args[2]) # MUL
        elif id_ == 7:  current += b(args[0])+b(args[1])+b(args[2]) # DIV
        elif id_ == 8: # IF
            if program[i].forced: addr = 8
            else: addr = args[0]
            current += b(addr)+b(program.index(goto[1]), 8)
        elif id_ == 9:  current += b(args[0])+b(args[1])+b(args[2]) # EQ
        elif id_ == 10: current += b(args[0])+b(args[1])+b(args[2]) # LT
        elif id_ == 11:
            op = ''.join([str(int(x == ['AND', 'ORR', 'XOR'].index(cmd))) for x in range(3)])
            current += op[0]+b(args[0], 3)+op[1]+b(args[1], 3)+op[2]+b(args[2], 3) # AND/ORR/XOR
        elif id_ == 12: current += b(args[0])+b(args[1])+'0'*4 # SCR
        elif id_ == 13: current += '0'*12 # RST
        elif id_ == 14: current += '0'*12 # END

        binary.append(current)

    return binary

all_vars = {}
temp_count = 0
TYPES = ['INT', 'BOOL']
start = time()

rom_size = 128 # commands = groups of 16 bits
ram_size = {'INT': 16, 'BOOL': 8}
filename, folder = ask_both('dikc')
log_init('compiling')

# get the file content
raw = get_raw(filename)

# get the commands in it
program, _ = get_cmd(raw)

# fix IF handling
program = use_goto(program)

# distribute ram slots
use_slots(program)

# convert commands into binary
binary = assemble(program)

# export to .ass, .bin and .litematic
export(''.join(binary), filename, folder, log)
log('Done')
log_wait()
