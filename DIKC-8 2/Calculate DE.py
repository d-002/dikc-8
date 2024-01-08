# DE: DIKC-8 equivalent.
# Way of completely subjectively estimate the computing power of a CPU,
# relatively to the DIKC-8. Even works with IRL CPUs.

def askb(text):
    while 1:
        a = input(text+' (y/n): ').lower()
        if a in 'yn' and a: return a == 'y'
        print('Please enter a valid answer.')

def askn(f, text, exclude=[]):
    while 1:
        try:
            a = f(input(text+' '))
            if not a: raise Exception
            if a in exclude: print('Cannot be', a)
            else: return a
        except: print('Please enter a number.')

mc = askb('Is the CPU in Minecraft?')
if mc: speed = 20*askn(float, 'What is the CPU\'s clock speed (cycles/s)?')
else: speed = 1
bit = askn(int, 'What is the word size?')
inst = askn(int, 'How many different instructions does the CPU have?')
io = askb('Does it have I/O ports?')
if io: io = askn(int, 'How many?')
rom = askn(int, 'How much ROM does it have, in bytes?')
ram = askn(int, 'How much RAM/registers does it have, in bytes?')
alu = askn(int, 'How many different instructions are in the ALU?')
mul = askb('Can the CPU do multiplication?')
if mul: mul = askn(int, 'In how many cycles?', [0])
div = askb('Can the CPU do division?')
if div: div = askn(int, 'In how many cycles?', [0])

DE = speed*inst*alu+io*20+rom/100+ram
if mul: DE += 20+1/mul
if div: DE += 50+1/div
DE *= bit/1772.48
input('The CPU\'s DE is %.3f.\nPress Enter to quit.' %DE)
