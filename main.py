import argparse
from emulator import CPU, Memory, RegisterFile
from assembler import Compiler


def stp_file_checker(s: str) -> str:
    if not s.endswith(".stp"):
        raise ValueError(f"'{s}' is not a stp file")
    return s


def bin_file_checker(s: str) -> str:
    if not s.endswith(".bin"):
        raise ValueError(f"'{s}' is not a bin file")
    return s


parser = argparse.ArgumentParser(
    description="Mein krasser Computer: Eine CPU Emulation mit eingebautem Assembler",
)
subparsers = parser.add_subparsers(dest="command", required=True)

compile_parser = subparsers.add_parser("compile", help="compile help")
compile_parser.add_argument("input", type=stp_file_checker, help="path to spt file")
compile_parser.add_argument(
    "-o",
    "--output",
    type=bin_file_checker,
    help="path to output file (default: './out.bin')",
    default="out.bin",
)

run_parser = subparsers.add_parser("run", help="run help")
run_parser.add_argument(
    "input",
    type=bin_file_checker,
    help="binary to run on eumlator (default out.bin)",
    default="out.bin",
    nargs="?",
)
run_parser.add_argument(
    "-pm",
    "--print-memory",
    type=int,
    nargs="*",
    help="print memory from given range (default range 0 100)",
)
run_parser.add_argument(
    "-pr", "--print-register", action="store_true", help="print reigsters"
)

ns = parser.parse_args()
if ns.command == "compile":
    c = Compiler(ns.input)
    c.build()
    c.output(ns.output)
elif ns.command == "run":
    m = Memory(2**16)
    m.load_from_file(ns.input)
    r = RegisterFile(10, 3)
    c = CPU(m, r)
    c.run()
    if ns.print_memory is not None:
        if len(ns.print_memory) == 0:
            m.print_bytes(0, 100)
        elif len(ns.print_memory) == 1:
            m.print_bytes(0, ns.print_memory[0])
        elif len(ns.print_memory) >= 2:
            m.print_bytes(ns.print_memory[0], ns.print_memory[1])
    if ns.print_register:
        print(r.registers)
