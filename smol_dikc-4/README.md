# smol DIKC-4

Schematic for the smol DIKC-4 Minecraft CPU.

This schematic also contains the program counter and reset modules, as well as a Fibonacci program and an attached 7-segment display.

## Instruction set

<table>
  <thead>
    <tr>
      <th colspan=3>Instruction</th>
      <th colspan=3>Operands</th>
    </tr>
    <tr>
      <th>Mnemonic</th>
      <th>Description</th>
      <th>Opcode</th>
      <th>Operand 0</th>
      <th>Operand 1</th>
      <th>Encoded value</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td>NOP</td>
      <td>No operation</td>
      <td>O or 4</td>
      <td><code>X</code></td>
      <td><code>X</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td>LDI</td>
      <td>Load immediate</td>
      <td>1</td>
      <td colspan=2>Value. registers where to store the value</td>
      <td>value = 4 * A + B</td>
    </tr>
    <tr>
      <td>ADD</td>
      <td>Puts a+b into ALU buffer</td>
      <td>2</td>
      <td>address for value a</td>
      <td>address for value b</td>
      <td>4 * a + b</td>
    </tr>
    <tr>
      <td>ABF</td>
      <td>Copies ALU buffer into RAM registers A and B</td>
      <td>3</td>
      <td>register A (address)</td>
      <td>register B (address)</td>
      <td>4 * A + B</td>
    </tr>
    <tr>
      <td>CPY</td>
      <td>Copies value in register src into dst</td>
      <td>5</td>
      <td>src (address)</td>
      <td>dst (address)</td>
      <td>4 * src + dst</td>
    </tr>
    <tr>
      <td>SUB</td>
      <td>Puts a-b into ALU buffer</td>
      <td>6</td>
      <td>address for value a</td>
      <td>address for value b</td>
      <td>4 * a + b</td>
    </tr>
    <tr>
      <td>HLT</td>
      <td>Halts program execution</td>
      <td>8</td>
      <td><code>X</code></td>
      <td><code>X</code></td>
      <td>0</td>
    </tr>
    <tr>
      <td><code>X</code></td>
      <td>Undefined instruction, do not use unless you know how the CPU works</td>
      <td>7</td>
      <td><code>X</code></td>
      <td><code>X</code></td>
      <td><code>X</code></td>
    </tr>
  </tbody>
</table>

`X` stands for undefined behaviour.

## How to fill the dikc-4 with stuff

To put instructions in the CPU, you need to fill two barrels for each instruction.  
The bottom barrel is for the opcode, and the top one is for the operand.

The bottom barrel can be filleed easily, but to fill the top one you will need to apply the formula as stated in the *Encoded value* column.

For example, say you want to copy the value from register 1 into register 2.

- `CPY` has the opcode `5`, so you would put `5` signal strength into the bottom barrel.
- Following the formula to encode the value, you should put `4 * src + dst` = `4 * 1 + 2` = `6` signal strength into the top barrel.

The first instruction is on the far left, then the next one is to its right.  
If no HLT instruction is specified, the program will loop until manually stopped.

Good luck!
