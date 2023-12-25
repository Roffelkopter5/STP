# Super Toller Pc

## Instructions

Each instruction gets encoded into 1 to 3 bytes according to its layout number `L` (0 through 7). While the Opcode (here `I`) gets encoded using 5 bits (so 32 Instructions total), so the first byte is always:

`LLLIIIII`

Registers (here `R`) take 4 bits and intermediates (here `V`) can be everywhere between 4 to 16 bits depending on the layout of the instruction.

The 8 possible Layouts are (`|`: Division, `-`: Compound):

* `L0` : `000IIIII | RRRR | RRRR | RRRR | RRRR`
* `L1` : `001IIIII | RRRR | RRRR | VVVV - VVVV`
* `L2` : `010IIIII | RRRR | VVVV - VVVV - VVVV`
* `L3` : `011IIIII | VVVV - VVVV - VVVV - VVVV`
* `L4` : `100IIIII | RRRR | RRRR`
* `L5` : `101IIIII | RRRR | XXXX`
* `L6` : `110IIIII | VVVV - VVVV`
* `L7` : `111IIIII`

Here is a list of all instructions:
| Name | Opcode | Layout  | Usage                 | Description                              |
| ---- | ------ | ------- | --------------------- | ---------------------------------------- |
| NOP  | 0      | L7      | NOP                   | No operation                             |
| ADD  | 1      | L0 / L1 | ADD dest, src1, src2  | Adds src1 and src2                       |
| ADDC | 2      | L0 / L1 | ADDC dest, src1, src2 | Adds src1 and sr2 with carry             |
| SUB  | 3      | L0 / L1 | SUB dest, src1, src2  | Subtracts src2 from src1                 |
| SUBB | 4      | L0 / L1 | SUBB dest, src1, src2 | Subtracts src2 from src1 with borrow     |
| SHL  | 5      | L0 / L1 | SHL dest, src1, src2  | Shifts src1 by src2 to the left          |
| SHR  | 6      | L0 / L1 | SHR dest, src1, src2  | Shifts src1 by src2 to the right         |
| SHA  | 7      | L0 / L1 | SHA dest, src1, src2  | Arithemticly shifts src1 by src2         |
| AND  | 8      | L0 / L1 | AND dest, src1, src2  | Bitwise and of src1 and src2             |
| OR   | 9      | L0 / L1 | OR dest, src1, src2   | Bitwise or of src1 and src2              |
| XOR  | 10     | L0 / L1 | XOR dest, src1, src2  | Bitwise xor of src1 and src2             |
| NOR  | 11     | L0 / L1 | NOR dest, src1, src2  | Bitwise nor of src1 and src2             |
| CMP  | 12     | L0 / L1 | CMP reg1, reg2        | Compares reg1 and reg2                   |
| INB  | 13     | L4      | INB reg, port         | Reads byte from port and puts it reg     |
| OUTB | 14     | L4      | OUTB reg, port        | Puts byte from reg on port               |
| LDB  | 15     | L2      | LDB reg, index        | Loads byte to reg at index               |
| LDA  | 16     | L3      | LDA addr              | Loads addr into index register           |
| STB  | 17     | L2      | STB reg, index        | Stores byte from reg at index            |
| MOV  | 18     | L4      | MOV dest, src         | Moves byte from src to dest              |
| PUSH | 19     | L5      | PUSH reg              | Pushes byte from reg onto the stack      |
| POP  | 20     | L5      | POP reg               | Pops byte from stack into reg            |
| JMP  | 21     | L3 / L2 | JMP addr              | Jumps to addr                            |
| JZ   | 22     | L3 / L2 | JZ addr               | Jumps if zero to addr                    |
| JNZ  | 23     | L3 / L2 | JNZ addr              | Jumps if not zero to addr                |
| JC   | 24     | L3 / L2 | JC addr               | Jumps if carry to addr                   |
| JNC  | 25     | L3 / L2 | JNC addr              | Jumps if not carry to addr               |
| JS   | 26     | L3 / L2 | JS addr               | Jumps if sign to addr                    |
| JNS  | 27     | L3 / L2 | JNS addr              | Jumps if not sign to addr                |
| CALL | 28     | L3 / L2 | CALL addr             | Changes stackframe and jumps (see below) |
| RET  | 29     | L7      | RET                   | Returns to prev stackframe (see below)   |
| INT  | 30     | L6      | INT num               | Triggers the interrupt num               |
| HLT  | 31     | L7      | HLT                   | Halts the proccesor                      |

## Registers

There are 13 8-bit registers that can directly be modififed and 3 16-bit registers that can not be directly modified. These are the 8-bit registers:

* `A` or `S1`, General purpose
* `B` or `S2`, General purpose
* `C` or `S3`, General purpose
* `D` or `S4`, General purpose
* `E` or `S5`, General purpose
* `X` or `T1`, Temporary
* `Y` or `T2`, Temporary
* `Z` or `T3`, Temporary
* `H`, High index register
* `L`, Low index register
* `F`, Flags
* `SP`, Stack pointer
* `MB`, Memory banking

These are the 16-bit registers:

* `IX`, Index register
* `FP`, Frame pointer
* `PC`, Programm counter

All general purpose registers (`S1`-`S5`) get saved during a call or interrupt, temporary registers (`T1`-`T3`) may be overwritten. All 16-biit registers can be pushed and poped but only the index register `IX` and the frame pointer `FP` can be used in the LDA (Load address) instruction. Only the index register can be directly used in arithemtic operations through the high `H` and low `L` registers. Furthermore the stack pointer `SP` is always relativ to the frame pointer `FP`, so the absolute stack pointer is at `FP + SP`.

## Memory

The System has a 16-bit address bus and a 8-bit data bus, so a memory size of 64 KiB. But this can be extended through banking. Devices or other external hardware can only be mapped into a memory bank higher than zero. For example in the default config vram gets mapped to memory bank 1.

Memory Layout:

* `0x0000 - 0x07EF` Restricted ROM
* `0x07F0 - 0x07FF` Interrupt vector table
* `0x0800 - 0x0FFF` General purpose ROM
* `0x1000 - 0x4FFF` Memory bank (GP RAM)
* `0x5000 - 0xEFFF` General purpose RAM
* `0xF000 - 0xFFFE` Stack (GP RAM)
* `0xFFFF - 0xFFFF` Device register

## Assembler

All relevant infos in 'example.stp'.

### Object files

Object files compiled from stp assembly are structured in the following way:

* `* bytes` Name of the stp file terminated with a `0` byte  
* `* bytes` Version string of the compiler terminated with `0` byte
* `1 byte` Compiler flags
* `2 bytes` Entry count in symbol table
* `* bytes` Symbol name terminated with `0` byte
* `2 bytes` Symbol address, `0xFFFF` if unknown
* `* bytes` All declared symbols
* `3 bytes` Terminating null bytes
* `* bytes` Machine code