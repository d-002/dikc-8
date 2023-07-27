##### DIKC language #####

# Instructions #
- int var = value/var (initialize new int variable to `value` or value of variable `var`)
- bool var = value/var (same)
- var = value/var (same, but for existing variable)
- if (condition) { do this }
- while (condition) { do this }

# Other info #
- variable names must only contain alphanumeric characters (not even `_`)
- int variables are 8 bits, bool variables are 0 or 1 (and not true or false)
- setting an variable value to `undefined` makes it reserve a memory slot for that variable
- operands:
  - +-*/ for usual operations
  - `&` for AND
  - `|` for OR
  - `^` for XOR
- /!\ No calculation priorities yet

##### ASS language #####

# Instructions #
- LDI a value (set value of int at address `a` to `value`)
- CPI a value (copy value of int `a` to `b`)
- LDB a value (LDI but for a bool variable)
- CPB a value (CPI but for bool)
- ADD a b c (add the values of int of address `a` and `b` and store result in address `c`)
- (same syntax for SUB, MUL, DIV)
- IFF a goto (if bool value is 1, go to line n°goto)
- EQU a b c (if int `a` and `b` are equal, bool of address `c` will be 1)
- LES a b c (same, but `c` is 1 when `a`<`b`)
- LGC AND/ORR/XOR a b c (logic operation of `a` and `b` stored into bool of address `c`)
- SRC a b (turn screen pixel (a, b) on, `a` and `b` are INT addresses)
- RST (reset all screen pixels to off)
- END (end the program execution)

# Other info #
- same as for DIKC (except concerning variables)
- addresses are integers
- to always redirect without the need of using a bool var, use `IFF 8 goto`
- lines are counted from the top, of index 0
- screen coordinates are 4-bit integers
