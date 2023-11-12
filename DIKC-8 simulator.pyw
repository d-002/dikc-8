# DIKC-08 = D_00's Incredible Keyboardless Computer

import pygame
from pygame.locals import *
from files.prompts import *

def mktiny(src):
    src = pygame.transform.smoothscale(src, (8, 8))
    dst = pygame.Surface((16, 16))
    for x in range(2):
        for y in range(2):
            dst.blit(src, (8*x, 8*y))
    return dst

def b(n):
    b = str(bin(int(n))).split('b')[1]
    return '0'*(8-len(b)) + b

def get_program(filename):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    data = ''.join(b(byte) for byte in data)
    program = []
    for x in range(0, len(data), 16):
        program.append(data[x:x+16])
    return program

def save_state():
    saved.append([
        {type_: ram[type_][:] for type_ in ram},
        [line[:] for line in dikc_screen],
        cmd_index,
        next_index])

def go_to_count():
    # go to a certain count state
    global cmd_index, next_index, ram, dikc_screen, count

    if count < len(saved): # use saved (already simulated)
        ram_, dikc_screen, cmd_index, next_index = saved[count]
        ram = {type_: ram_[type_][:] for type_ in ram_}
        dikc_screen = [line[:] for line in dikc_screen]

    else: # simulate and go to (new count)
        if int(program[cmd_index][:4], 2) == 14: # END: do nothing
            count -= 1
            return

        cmd_index, next_index = next_index, simulate(next_index)
        save_state()

def simulate(i):
    cmd = program[i]
    cmd_id = int(cmd[:4], 2)
    a, b, c = (int(cmd[x:x+4], 2) for x in range(4, 16, 4))

    next_ = i+1
    if cmd_id == 0: ram['INT'][a] = b*16 + c
    elif cmd_id == 1: ram['INT'][c] = ram['INT'][b]
    elif cmd_id == 2: ram['BOOL'][a] = int(b/8)
    elif cmd_id == 3: ram['BOOL'][c] = ram['BOOL'][a]
    elif cmd_id == 4: ram['INT'][c] = (ram['INT'][a]+ram['INT'][b])%256
    elif cmd_id == 5: ram['INT'][c] = (ram['INT'][a]-ram['INT'][b])%256
    elif cmd_id == 6: ram['INT'][c] = (ram['INT'][a]*ram['INT'][b])%256
    elif cmd_id == 7:
        if ram['INT'][b] == 0: ram['INT'][c] = 255 # division by 0
        else: ram['INT'][c] = int(ram['INT'][a]/ram['INT'][b])
    elif cmd_id == 8: # IF
        if a//8 or ram['BOOL'][a]:
            next_ = b*16 + c
    elif cmd_id == 9: ram['BOOL'][c] = ram['INT'][a] == ram['INT'][b]
    elif cmd_id == 10: ram['BOOL'][c] = ram['INT'][a] < ram['INT'][b]
    elif cmd_id == 11: # logic
        if cmd[4] == '1': ram['BOOL'][c%8] = ram['BOOL'][a%8] and ram['BOOL'][b%8]
        if cmd[8] == '1': ram['BOOL'][c%8] = ram['BOOL'][a%8] or ram['BOOL'][b%8]
        if cmd[12] == '1': ram['BOOL'][c%8] = ram['BOOL'][a%8] ^ ram['BOOL'][b%8]
    elif cmd_id == 12: dikc_screen[ram['INT'][b]%16][ram['INT'][a]%16] = 1 # write in screen
    elif cmd_id == 13: # reset screen
        for line in dikc_screen:
            for x in range(16):
                line[x] = 0
    elif cmd_id == 14:
        next_ = i # END

    return next_

def draw_info():
    # show redstone lamps for variables
    X = 60
    text = mcfont.render('BOOL', True, white)
    screen.blit(text, (X - text.get_width()/2, 20))
    for y in range(8):
        text = mcfont.render(str(7-y), True, white)
        screen.blit(text, (X - 40, 80 + 32*y))
        screen.blit(lamps[ram['BOOL'][7-y]], (X-8, 80 + 32*y))

    X = 130
    text = mcfont.render('INT', True, white)
    screen.blit(text, (X + 240 - text.get_width()/2, 20))
    screen.blit(mcfont.render('Values:', True, white), (40, 330))
    for x in range(16):
        text = mcfont.render(str(x), True, white)
        screen.blit(text, (X + 32*x - text.get_width()/2, 50))
        n = b(ram['INT'][x])
        for y in range(8):
            screen.blit(lamps[n[y] == '1'], (X + 32*x - 8, 80 + 32*y))

        # show value in decimal
        text = mcfont.render(str(ram['INT'][x]), True, white)
        screen.blit(text, (X + 32*x - text.get_width()/2, 330))

    # draw screen
    X = 650
    text = mcfont.render('Screen', True, white)
    screen.blit(text, (X + 128 - text.get_width()/2, 20))
    for x in range(16):
        for y in range(16):
            screen.blit(tinylamps[dikc_screen[15-y][x]], (X + 16*x, 72 + 16*y))

    # show additional info
    y = 370
    def info(text):
        nonlocal y
        screen.blit(font.render(text, True, white), (20, y))
        y += 16
    info('Current instruction index: %d' %cmd_index)
    info('Total instructions run: %d' %count)
    info('Current instruction: %s' %program[cmd_index])
    cmd_id = int(program[cmd_index][:4], 2)
    info('Command: %s (ID %d)' %(commands[cmd_id], cmd_id))

program = get_program(ask_one('bin'))
commands = ['LDI', 'CPI', 'LDB', 'CPB', 'ADD', 'SUB', 'MUL', 'DIV',
            'IFF', 'EQU', 'LES', 'LGC', 'SCR', 'RST', 'END']

ram = {type_: [0 for _ in range(size)] for type_, size in (('INT', 16), ('BOOL', 8))}
dikc_screen = [[0 for x in range(16)] for y in range(16)]
saved = [] # when executing a command, make a copy to go back to
count = cmd_index = next_index = 0 # index in saved
go_to_count()

black, white = (10, 10, 10), (255, 255, 255)
pygame.init()

screen = pygame.display.set_mode((950, 450))
clock = pygame.time.Clock()
pygame.display.set_caption('DIKC-8 Simulator')
pygame.key.set_repeat(300, 25)

mcfont = pygame.font.Font('files/font.ttf', 16)
font = pygame.font.SysFont('consolas', 16)
lamps = [pygame.image.load('files/lamp_%s.png' %state) for state in ['off', 'on']]
tinylamps = [mktiny(l) for l in lamps]

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()
        elif event.type == KEYDOWN:
            if event.key == K_LEFT and count > 0:
                count -= 1
            elif event.key == K_RIGHT:
                count += 1
            go_to_count()

    screen.fill(black)
    draw_info()
    pygame.display.flip()
    clock.tick(60)
