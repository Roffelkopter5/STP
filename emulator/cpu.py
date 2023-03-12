from .memory import Memory
from .register_file import RegisterFile
from enum import IntFlag, auto, Enum

Address = int


class OpCode(Enum):
    NOP = 0

    ADD = auto()
    ADDC = auto()
    SUB = auto()
    SUBB = auto()
    SHL = auto()
    SHR = auto()
    SHA = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    NOR = auto()  # 11

    CMP = auto()  # 12

    INB = auto()
    OUTB = auto()  # 14

    LDB = auto()
    STB = auto()  # 16

    JMP = auto()  # 17
    JZE = auto()
    JNZ = auto()
    JCA = auto()
    JNC = auto()
    JSN = auto()
    JNS = auto()  # 23

    INT = 30
    HLT = 31


class Flag(IntFlag):
    CARRY = auto()
    SIGN = auto()
    ZERO = auto()


class CPU:
    def __init__(self, memory: Memory, register_file: RegisterFile):
        self.memory = memory
        self.registers = register_file
        self.pc = 0
        self.flags = Flag(0)
        self.sp = 0
        self.instr_buffer = 0
        self.opcode = OpCode(1)
        self.running = False

    # region Helper functions
    def set_flag(self, flag: Flag):
        self.flags |= flag

    def remove_flag(self, flag: Flag):
        if self.is_flag_set(flag):
            self.flags ^= flag

    def is_flag_set(self, flag: Flag) -> bool:
        return flag in self.flags

    def PC(self) -> Address:
        pc = self.pc
        self.pc += 1
        return pc

    # endregion
    # region Instruction pipeline
    def fetch_instr(self):
        self.instr_buffer = 0
        for i in range(2, -1, -1):
            self.instr_buffer |= self.memory.load_byte(self.PC()) << (8 * i)

    def decode_instr(self):
        # 000IIIII | DDDD SSSS SSSS XXXX
        # 001IIIII | DDDD SSSS VVVV VVVV
        # 010IIIII | DDDD VVVV VVVV VVVV
        # 011IIIII | VVVV VVVV VVVV VVVV
        layout = (self.instr_buffer >> 22) & 0b11
        self.opcode = OpCode((self.instr_buffer >> 17) & 0b11111)
        if layout == 0:
            self.decode_L0()
        elif layout == 1:
            self.decode_L1()
        elif layout == 2:
            self.decode_L2()
        elif layout == 3:
            self.decode_L3()

    def decode_L0(self):
        self.decoded_args = {
            "dest": (self.instr_buffer >> 13) & 0xF,
            "src1": (self.instr_buffer >> 9) & 0xF,
            "src2": (self.instr_buffer >> 5) & 0xF,
        }

    def decode_L1(self):
        self.decoded_args = {
            "dest": (self.instr_buffer >> 13) & 0xF,
            "src1": (self.instr_buffer >> 9) & 0xF,
            "val": (self.instr_buffer >> 1) & 0xFF,
        }

    def decode_L2(self):
        self.decoded_args = {
            "dest": (self.instr_buffer >> 13) & 0xF,
            "val": (self.instr_buffer >> 1) & 0xFFF,
        }

    def decode_L3(self):
        self.decoded_args = {
            "val": (self.instr_buffer >> 1) & 0xFFFF,
        }

    def execute_instr(self):
        self.fetch_instr()
        self.decode_instr()
        if f := getattr(self, self.opcode.name.lower() + "_", None):
            f()
        else:
            print(f"'{self.opcode.name}' not implemented!")

    def update_flags(self, value: int):
        if value == 0:
            self.set_flag(Flag.ZERO)
        else:
            self.remove_flag(Flag.ZERO)
        if value > 0xFF:
            self.set_flag(Flag.CARRY)
        else:
            self.remove_flag(Flag.CARRY)
        if value & 0x80 > 1:
            self.set_flag(Flag.SIGN)
        else:
            self.remove_flag(Flag.SIGN)

    def load_operands(self) -> tuple[int, int, int]:
        d = self.decoded_args["dest"]
        a = self.registers.get_register(self.decoded_args["src1"])
        if "src2" in self.decoded_args:
            b = self.registers.get_register(self.decoded_args["src2"])
        else:
            b = self.decoded_args["val"]
        return d, a, b

    # endregion
    # region Instruction implementations

    def hlt_(self):
        self.running = False

    def nop_(self):
        return

    def arithmetic(self, o):
        d, a, b = self.load_operands()
        res = o(a, b)
        self.update_flags(res)
        self.registers.set_register(d, res)

    def add_(self):
        self.arithmetic(lambda a, b: a + b)

    def addc_(self):
        self.arithmetic(lambda a, b: a + b + (1 if self.is_flag_set(Flag.CARRY) else 0))

    def sub_(self):
        self.arithmetic(lambda a, b: a - b)

    def subb_(self):
        self.arithmetic(lambda a, b: a - b - (1 if self.is_flag_set(Flag.SIGN) else 0))

    def shl_(self):
        self.arithmetic(lambda a, b: a << b)

    def shr_(self):
        self.arithmetic(lambda a, b: a >> b)

    # TODO sha_

    def and_(self):
        self.arithmetic(lambda a, b: a & b)

    def or_(self):
        self.arithmetic(lambda a, b: a | b)

    def xor_(self):
        self.arithmetic(lambda a, b: a ^ b)

    def nor_(self):
        self.arithmetic(lambda a, b: ~(a | b))

    ...

    def jmp_(self):
        self.pc = self.decoded_args["val"]

    def jze_(self):
        if self.is_flag_set(Flag.ZERO):
            self.jmp_()

    def jnz_(self):
        if not self.is_flag_set(Flag.ZERO):
            self.jmp_()

    # endregion

    def run(self):
        self.running = True
        while self.running:
            self.execute_instr()

    ...
