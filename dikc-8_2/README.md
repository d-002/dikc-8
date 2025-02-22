# DIKC-8 2

README for the second iteration of the DIKC-8.  
Major changes and optimizations done, for almost every part of the CPU.

Video coming soon(tm).

### See trailer on YouTube [upcoming]

## Calculate DE
"DE": "DIKC-8 equivalent".

This is my way to completely subjectively estimate the computing power of a CPU, relatively to the DIKC-8. The DIKC-8's DE is 1.

This should work for IRL CPUs, with, again, a lot of very arbitrary settings.

## `ass2` file extension and language

### General

This is an assembly language. Convert code into a [schematic](https://www.curseforge.com/minecraft/mc-mods/litematica) with the assembler (`ass2schem.py`) to import into the CPU's ROM.

### Syntax

- One instruction per line. Instruction code, then arguments, separated by:
  - at least one space in between the instruction and the first argument
  - a comma (and possibly spaces) in between the different arguments

- Indentation doesn't matter, as well as duplicate spaces

- Comments: everything after a semicolon (`;`) is ignored on every line  
  Example:  
  ```ass2
  ADD 0 1 ; add the values in registers 0 and 1 and store in arith. buffer
  ```

- Defining jump points: just write the label name and a colon (`:`) after it  
  Example:  
  ```ass2
  WRT 0, 0  ; initial count
  WRT 1, 1  ; decrement amount
  WRT 2, 10 ; stop threshold
  loop:
      ADD 0, 1
      ABF 0
      LES 0 2
      JPI loop
  HLT
  ```

- Defining variables: `.def name = value`  
  Example:  
  ```ass2
  .def a = 0
  ```

- On the use of NOP:
> [!WARNING]
> It is your respondibility to use NOP for multiple-cycle instructions. Some instructions can be run in parallel, use this at rouy own risk!

## Help for `ass2schem.py`:

```
ass2 to schematic

Usage:
    - ass2schem [-f] filename [-w value] [-p value] [-c value]
    - ass2schem -h command
    - ass2schem -d -m/-w/-p/-c value
Arguments:
    No args        Display help.
    [-f] file      Export "file" to schematic (e.g. py ass2schem myfile.ass2)
    -h command     Display instruction help (e.g. py ass2schem -h WRT)
    -d arg value   Set default value for argument to value (value: 0/1)
    -m path        Path to minecraft .minecraft folder
    -w value       Display warnings
    -p value       Display program code
    -c value       Use colors
```

Instructions (use `_help(command name)` in the exporter):

## WRT (code 0):
```
Writes 5-bit value to register
  Syntax: WRT a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Short value (between 0 and 31)
```

## CPY (code 1):
```
Copies register a to register b
  Syntax: CPY a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## BIT (code 2):
```
Sets bit of register a at index b (0: least significant) to value c
  Syntax: BIT a b c
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Bit index (between 0 and 7)
    | - c: Single bit (between 0 and 1)
```

## SDB (code 3):
```
Sets data buffer (used to then store 8-bit values in registers, see DBF)
  Syntax: SDB a
  Arguments:
    | - a: Number (between 0 and 255)
```

## SCB (code 4):
```
Sets compare buffer to register a's bit at index b (0: least significant)
  Syntax: SCB a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Bit index (between 0 and 7)
```

## DBF (code 5):
```
Data buffer to register
  Syntax: DBF a
  Arguments:
    | - a: Number (between 0 and 255)
```

## ABF (code 6):
```
ALU buffer to register
  Syntax: ABF a
  Arguments:
    | - a: Number (between 0 and 255)
```

## CBF (code 7):
```
Compare buffer to register a at bit of index b (0: least significant)
  Syntax: CBF a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Bit index (between 0 and 7)
```

## EQU (code 8):
```
Sets compare buffer to register a == register b
Takes 2 cycles
  Syntax: EQU a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## MOR (code 9):
```
Sets compare buffer to register a > register b
Takes 2 cycles
  Syntax: MOR a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## LES (code 10):
```
Sets compare buffer to register a < register b
Takes 2 cycles
  Syntax: LES a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## LSH (code 11):
```
Left shift (multiplication by 2) into ALU buffer
Takes 2 cycles
  Syntax: LSH a
  Arguments:
    | - a: Address (between 0 and 31)
```

## RSH (code 12):
```
Right shift (integer division by 2) into ALU buffer
Takes 2 cycles
  Syntax: RSH a
  Arguments:
    | - a: Address (between 0 and 31)
```

## SUB (code 13):
```
Puts a-b into ALU buffer
Takes 2 cycles
  Syntax: SUB a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## ADD (code 14):
```
Puts a+b into ALU buffer
Takes 2 cycles
  Syntax: ADD a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## NOT (code 15):
```
Bitwise NOT into ALU buffer
Takes 2 cycles
  Syntax: NOT a
  Arguments:
    | - a: Address (between 0 and 31)
```

## ORR (code 16):
```
Bitwise OR into ALU buffer
Takes 2 cycles
  Syntax: ORR a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## AND (code 17):
```
Bitwise AND into ALU buffer
Takes 2 cycles
  Syntax: AND a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## XOR (code 18):
```
Bitwise XOR into ALU buffer
Takes 2 cycles
  Syntax: XOR a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## JPI (code 20):
```
Jumps to address if the compare buffer is True
Takes 2 cycles
  Syntax: JPI a
  Arguments:
    | - a: Program counter address (between 0 and 127)
```

## JMP (code 21):
```
Jumps to address
Takes 2 cycles
  Syntax: JMP a
  Arguments:
    | - a: Program counter address (between 0 and 127)
```

## OUT (code 22):
```
Writes value to I/O port
  Syntax: OUT a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: IO address (between 0 and 7)
```

## OUP (code 23):
```
Pulses (writes number, then writes a 0) to I/O port
  Syntax: OUP a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: IO address (between 0 and 7)
```

## INN (code 24):
```
Writes I/O port value into register
  Syntax: INN a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: IO address (between 0 and 7)
```

## MUL (code 25):
```
Puts a*b into ALU buffer
Takes 3 cycles
  Syntax: MUL a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## DIV (code 26):
```
Puts a/b (integer division) into ALU buffer
Takes 3 cycles
  Syntax: DIV a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## MOD (code 27):
```
Puts a%b into ALU buffer
Takes 3 cycles
  Syntax: MOD a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## HLT (code 28):
```
Stops the program's execution
  Syntax: HLT
  Arguments: [no arguments]
```

## NOP (code 29):
```
Stalls for one cycle
  Syntax: NOP
  Arguments: [no arguments]
```

## PUS (code 30):
```
Push the current program counter value into the call stack
  Syntax: PUS
  Arguments: [no arguments]
```

## POP (code 31):
```
Put the latest (default 0) call stack value into the program counter
  Syntax: POP
  Arguments: [no arguments]
```
