from __future__ import annotations
from enum import Enum, auto
from tokenizer import Tokenizer, Token, TokenType
from dataclasses import dataclass, field


class ParsingError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class NodeType(Enum):
    ROOT = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    INSTR = auto()
    VALUE = auto()
    LABEL = auto()
    DIRECTIVE = auto()
    PREPROCESSOR = auto()


class ArgType(Enum):
    REGISTER = auto()
    INDEX_REGISTER = auto()
    IMMEDIATE_8 = auto()
    IMMEDIATE_12 = auto()
    IMMEDIATE_16 = auto()


@dataclass
class Node:
    node_type: NodeType
    value: any = None
    tokens: list[Token] = field(repr=False, default_factory=list)
    children: list[Node] = field(repr=False, default_factory=list)


@dataclass
class InstrDef:
    signature: tuple[ArgType]
    layout: int


SIG_2 = (ArgType.REGISTER, ArgType.IMMEDIATE_12)
SIG_2 = ArgType.IMMEDIATE_16

ARITHMETIC_INSTR = {
    "ADD",
    "ADDC",
    "SUB",
    "SUBB",
    "SHL",
    "SHR",
    "SHA",
    "AND",
    "OR",
    "XOR",
    "NOR",
}

MEMORY_INSTRUCTIONS = {"LDB", "STB"}

JUMP_INSTR = {"JMP", "JZE", "JNZ", "JCA", "JNC", "JSN", "JNS"}

INSTRUCTION_SET = ARITHMETIC_INSTR | MEMORY_INSTRUCTIONS | JUMP_INSTR

INSTRUCTION_DEF = {}


def APPEND_INSTR_DEF(instrs, instr_defs):
    global INSTRUCTION_DEF
    for instr in instrs:
        INSTRUCTION_DEF[instr] = instr_defs


APPEND_INSTR_DEF(
    ARITHMETIC_INSTR,
    (
        InstrDef((ArgType.REGISTER, ArgType.REGISTER, ArgType.REGISTER), 0),
        InstrDef((ArgType.REGISTER, ArgType.REGISTER, ArgType.IMMEDIATE_8), 1),
    ),
)

APPEND_INSTR_DEF(MEMORY_INSTRUCTIONS, ())  # TODO: Restructure memory instructions

APPEND_INSTR_DEF(JUMP_INSTR, (InstrDef((ArgType.IMMEDIATE_16,), 3),))


class Parser:
    def __init__(self, *, path: str = "", buffer: str = ""):
        if path != "":
            with open(path, "r") as f:
                buffer = f.read()
        self.tokenizer = Tokenizer(buffer)
        self.root = Node(NodeType.ROOT)

    def parse(self):
        token = self.tokenizer.peek_next_token()
        while token:
            token_type = token.token_type
            if token_type == TokenType.DIRECTIVE:
                node = self.parse_directive()
            elif token_type == TokenType.LABEL:
                self.tokenizer.get_next_token()
                node = Node(NodeType.LABEL, token.value[:-1], [token], None)
            elif token_type == TokenType.PREPROCESSOR:
                node = self.parse_preprocessor()
            elif token_type == TokenType.IDENTIFIER:
                node = self.parse_instruction()
            self.root.children.append(node)
            token = self.tokenizer.peek_next_token()

    def parse_directive(self):
        pass

    def parse_preprocessor(self):
        pass

    def parse_instruction(self):
        instr_token = self.tokenizer.get_next_token()
        instr = instr_token.value.upper()
        if instr not in INSTRUCTION_SET:
            raise ParsingError(f"Unknown Instruction '{instr}'!")
        instr_defs = INSTRUCTION_DEF[instr]
        print(instr_defs)

    def body(self) -> list[Node]:
        return self.root.children

    def print_node(self, n, level):
        print(f"{' ' * level}{'-' if n.children else ' '} {n}")
        if n.children:
            for child in n.children:
                self.print_node(child, level + 1)

    def print_ast(self):
        self.print_node(self.root, 0)


p = Parser(buffer="ADD")
p.parse()
