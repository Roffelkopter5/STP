from .stp_parser import Parser, Node
from .tokenizer import Token, TokenType

OPCODES = {
    "NOP": 0,
    "ADD": 1,
    "ADDC": 2,
    "SUB": 3,
    "SUBB": 4,
    "SHL": 5,
    "SHR": 6,
    "SHA": 7,
    "AND": 8,
    "OR": 9,
    "XOR": 10,
    "NOR": 11,
    "JMP": 28,
    "JZE": 29,
    "JNZ": 30,
    "HLT": 31,
}


class CompilationError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class Compiler:
    def __init__(self, path: str) -> None:
        self.parser = Parser(path)
        self.parser.parse()
        self.buffer = bytearray()
        self.labels = {}
        self.instr_counter = 0
        self.last_instr = None

    def build(self):
        for node in self.parser.body():
            if node.token.token_type == TokenType.INSTRUCTION:
                self.add_data(self.build_instruction(node), 3)
            elif node.token.token_type == TokenType.LABEL:
                self.set_label(node.token)

    def set_label(self, t: Token):
        if t.value not in self.labels:
            self.labels[t.value] = self.instr_counter + 1
        else:
            raise CompilationError(f"Label '{t.value}' already exists!")

    def get_register_index(self, t: Token) -> int:
        if t.token_type == TokenType.REGISTER:
            reg = int(t.value[1:])
            if reg > 15:
                raise CompilationError(
                    f"Cannot compile '{t.value}'! Max register index is 15"
                )
            return reg

    def get_imm(self, t: Token, size: int):
        v = int(t.value)
        # if len(bin(v)) > size:
        #     print("Warning: integer values should not exceed 255")
        return v & (2**size - 1)

    # TODO: Better Layout/Signature System. It's a total mess
    def build_instruction(self, node: Node):
        opcode = OPCODES[node.token.value]
        instruction = opcode << 17
        sig = node.children[0]
        assert sig.token.token_type == TokenType.SIGNATURE
        layout = (int(sig.token.value[0][1:])) & 0b11
        instruction |= layout << 22
        reg = val = 0
        for i, s in enumerate(sig.token.value[1:]):
            if s == "RD":
                reg = self.get_register_index(node.children[i + 1].token)
                instruction |= reg << 13
            elif s == "RS1":
                reg = self.get_register_index(node.children[i + 1].token)
                instruction |= reg << 9
            elif s == "RS2":
                reg = self.get_register_index(node.children[i + 1].token)
                instruction |= reg << 5
            elif s == "I8":
                val = self.get_imm(node.children[i + 1].token, 8)
                instruction |= val << 1
            elif s == "I16":
                val = self.get_imm(node.children[i + 1].token, 16)
                instruction |= val << 1
        # if len(node.children) == 3:
        # dest = self.get_register_index(node.children[0].token)
        # instruction |= dest << 13
        # src1 = self.get_register_index(node.children[1].token)
        # instruction |= src1 << 9
        # t = node.children[2].token
        # if t.token_type == TokenType.REGISTER:
        #     src2 = self.get_register_index(t)
        #     instruction |= src2 << 5
        # else:
        #     val = self.get_imm(t, 8)
        #     instruction |= val << 1
        #     instruction |= 0b01 << 22
        # elif len(node.children) == 1:
        #     val = self.get_imm(node.children[0].token, 16)
        #     instruction |= val << 1
        #     instruction |= 0b11 << 22
        self.instr_counter += 1
        self.last_instr = node.token.value
        return instruction

    def add_data(self, data: int, byte_count: int):
        local_buffer = bytearray()
        for i in range(byte_count - 1, -1, -1):
            local_buffer.append((data >> (8 * i)) & 0xFF)
        self.buffer.extend(local_buffer)

    def output(self, path: str):
        with open(path, "wb") as f:
            f.write(self.buffer)
