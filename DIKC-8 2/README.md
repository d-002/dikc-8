# DIKC-8 2

README for the second iteration of the DIKC-8.  
Major changes and optimizations done, for almost every part of the CPU.

### See trailer on YouTube [upcoming]

## `ass2` extension and language

This is an assembly language, with the ability to easily convert into a [schematic](https://www.curseforge.com/minecraft/mc-mods/litematica) and import into the CPU's ROM.

Help for `ass2schem.py`:

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

## WRT
```
  Writes 5-bit value to register
  Syntax: WRT a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Short value (between 0 and 31)
```

## CPY
```
  Copies register a to register b
  Syntax: CPY a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## BIT
```
  Sets bit of register a at index b (0: least significant) to value c
  Syntax: BIT a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Bit index (between 0 and 7)
```

## SDB
```
  Sets data buffer (used to then store 8-bit values in registers, see DBF)
  Syntax: SDB a
  Arguments:
    | - a: Number (between 0 and 255)
```

## SCB
```
  Sets compare buffer to register a's bit at index b (0: least significant)
  Syntax: SCB a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Bit index (between 0 and 7)
```

## DBF
```
  Data buffer to register
  Syntax: DBF a
  Arguments:
    | - a: Number (between 0 and 255)
```

## ABF
```
  ALU buffer to register
  Syntax: ABF a
  Arguments:
    | - a: Number (between 0 and 255)
```

## CBF
```
  Compare buffer to register a at bit of index b (0: least significant)
  Syntax: CBF a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Bit index (between 0 and 7)
```

## EQU
```
  Sets compare buffer to register a == register b
Takes 2 cycles
  Syntax: EQU a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## MOR
```
  Sets compare buffer to register a > register b
Takes 2 cycles
  Syntax: MOR a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## LES
```
  Sets compare buffer to register a < register b
Takes 2 cycles
  Syntax: LES a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## LSH
```
  Left shift (multiplication by 2) into ALU buffer
Takes 2 cycles
  Syntax: LSH a
  Arguments:
    | - a: Address (between 0 and 31)
```

## RSH
```
  Right shift (integer division by 2) into ALU buffer
Takes 2 cycles
  Syntax: RSH a
  Arguments:
    | - a: Address (between 0 and 31)
```

## SUB
```
  Puts a-b into ALU buffer
Takes 2 cycles
  Syntax: SUB a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## AND
```
  Puts a+b into ALU buffer
Takes 2 cycles
  Syntax: ADD a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## NOT
```
  Bitwise NOT into ALU buffer
Takes 2 cycles
  Syntax: NOT a
  Arguments:
    | - a: Address (between 0 and 31)
```

## ORR
```
  Bitwise OR into ALU buffer
Takes 2 cycles
  Syntax: ORR a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## AND
```
  Bitwise AND into ALU buffer
Takes 2 cycles
  Syntax: AND a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## XOR
```
  Bitwise XOR into ALU buffer
Takes 2 cycles
  Syntax: XOR a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## JPI
```
  Jumps to address if the compare buffer is True
Takes 2 cycles
  Syntax: JPI a
  Arguments:
    | - a: Program counter address (between 0 and 127)
```

## JMP
```
  Jumps to address
Takes 2 cycles
  Syntax: JMP a
  Arguments:
    | - a: Program counter address (between 0 and 127)
```

## OUT
```
  Writes value to I/O port
  Syntax: OUT a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: IO address (between 0 and 7)
```

## OUP
```
  Pulses (writes number, then writes a 0) to I/O port
  Syntax: OUP a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: IO address (between 0 and 7)
```

## INN
```
  Writes I/O port value into register
  Syntax: INN a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: IO address (between 0 and 7)
```

## MUL
```
  Puts a*b into ALU buffer
Takes 3 cycles
  Syntax: MUL a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## DIV
```
  Puts a/b (integer division) into ALU buffer
Takes 3 cycles
  Syntax: DIV a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## MOD
```
  Puts a%b into ALU buffer
Takes 3 cycles
  Syntax: MOD a b
  Arguments:
    | - a: Address (between 0 and 31)
    | - b: Address (between 0 and 31)
```

## END
```
  Stops the program's execution
  Syntax: END
  Arguments: [no arguments]
```

## NOP
```
  Stalls for one cycle
  Syntax: NOP
  Arguments: [no arguments]
```

## PUS
```
  Push the current program counter value into the call stack
  Syntax: PUS
  Arguments: [no arguments]
```

## POP
```
  Put the latest (default 0) call stack value into the program counter
  Syntax: POP
  Arguments: [no arguments]
```
