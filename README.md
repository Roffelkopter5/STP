# Super Toller Pc

## Compile
`python main.py compile <FILENAME>` File must be a '.stp' file

`-o <OUTPUT_FILE>` or `--output <OUTPUT_FILE>` Outputs machine code to output file. Output file must be a '.bin' file.

`-h` or `--help` for help 


## Run
`python main.py run <FILENAME>` File must be a '.bin' file (default is 'out.bin')

`-pr` or `--print-register` Prints out the registers.

`-pm a [b]` or `--print-memory a [b]` Prints out memory from a to b, or 0 to a (a default is 100). 

`-h` or `--help` for help

## Assembler
All relevant infos in 'example.stp'.