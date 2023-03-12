from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
import re


class TokenizationError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class ParsingError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class TokenType(Enum):
    OPERATOR = auto()
    OPEN_PARAN = auto()
    CLOSE_PARAN = auto()
    INT = auto()
    BIN = auto()
    HEX = auto()
    CHAR = auto()


@dataclass
class Token:
    token_type: TokenType
    value: str

    def __str__(self) -> str:
        return f"Token({self.token_type}, '{self.value}')"


TOKEN_DEFINTIONS = {
    TokenType.OPERATOR: re.compile(r"^\+|-|\*|/|\||&|~|\^"),
    TokenType.OPEN_PARAN: re.compile(r"^\("),
    TokenType.CLOSE_PARAN: re.compile(r"^\)"),
    TokenType.HEX: re.compile(r"^0X[0-9A-F]+"),
    TokenType.BIN: re.compile(r"^0B[01]+"),
    TokenType.INT: re.compile(r"^\d+"),
    TokenType.CHAR: re.compile(r"^'[A-Z]'"),
}

OP_PRESEDENCE = {"|": 0, "^": 1, "&": 2, "+": 3, "-": 3, "*": 4, "/": 5}

BIN_OP_FUNC = {
    "+": lambda r, l: r + l,
    "-": lambda r, l: r - l,
    "*": lambda r, l: r * l,
    "/": lambda r, l: r // l,
    "|": lambda r, l: r | l,
    "&": lambda r, l: r & l,
}

UNARY_OPS = ["-", "~"]

UN_OP_FUNC = {"-": lambda v: -v, "~": lambda v: ~v}

COMMENT = re.compile(r"^\s*(#[^\n]*|\s+)")


class Tokenizer:
    def __init__(self, buffer: str) -> None:
        self.buffer = buffer.strip().upper()
        self.pointer = 0
        self.buff_len = len(self.buffer)
        self.curr_token = self.scan_token()

    def peek_next_token(self):
        return self.curr_token

    def get_next_token(self):
        current = self.curr_token
        self.scan_token()
        return current

    def scan_token(self):
        while m := re.match(COMMENT, self.buffer[self.pointer :]):
            self.pointer += m.end()
        if self.pointer >= self.buff_len:
            self.curr_token = None
            return None
        for token_type, token_def in TOKEN_DEFINTIONS.items():
            if m := re.match(token_def, self.buffer[self.pointer :]):
                self.pointer += m.end()
                t = Token(token_type, m[0])
                self.curr_token = t
                return t
        raise TokenizationError(
            f"Unknown Token at '{self.buffer[self.pointer:self.pointer+20]}'"
        )


@dataclass
class Node:
    name: str
    value: any
    children: list[Node] = field(repr=False)


def parse_primary(t: Tokenizer):
    token = t.get_next_token()
    if token is None:
        raise ParsingError()
    if token.token_type == TokenType.OPERATOR and token.value in UNARY_OPS:
        val = parse_primary(t)
        return Node("UN_OP", token.value, [val])
    if token.token_type == TokenType.OPEN_PARAN:
        node = parse_expression(t)
        token = t.get_next_token()
        if token.token_type != TokenType.CLOSE_PARAN:
            raise ParsingError()
        return node
    elif token.token_type == TokenType.INT:
        return Node("VAL", int(token.value), None)
    elif token.token_type == TokenType.HEX:
        return Node("VAL", int(token.value, 16), None)
    elif token.token_type == TokenType.BIN:
        return Node("VAL", int(token.value, 2), None)
    elif token.token_type == TokenType.CHAR:
        return Node("VAL", ord(token.value[1]), None)
    elif token.token_type == TokenType.ID:
        return Node("ID", token.value, None)
    else:
        raise ParsingError()


def parse_expression(t: Tokenizer, p=0, lhs=None):
    if lhs is None:
        lhs = parse_primary(t)
    token = t.peek_next_token()
    while (
        token
        and token.token_type == TokenType.OPERATOR
        and OP_PRESEDENCE[token.value] >= p
    ):
        op = t.get_next_token()
        rhs = parse_primary(t)
        token = t.peek_next_token()
        while (
            token
            and token.token_type == TokenType.OPERATOR
            and OP_PRESEDENCE[token.value] >= OP_PRESEDENCE[op.value] + 1
        ):
            rhs = parse_expression(t, p + 1, rhs)
            token = t.peek_next_token()
        lhs = Node("BIN_OP", op.value, [lhs, rhs])
    return lhs


def print_node(n: Node, level):
    print(f"{' ' * level}{'-' if n.children else ' '} {n}")
    if n.children:
        for child in n.children:
            print_node(child, level + 1)


def eval_node(n: Node):
    if n.name == "BIN_OP":
        return BIN_OP_FUNC[n.value](eval_node(n.children[0]), eval_node(n.children[1]))
    elif n.name == "UN_OP":
        return UN_OP_FUNC[n.value](eval_node(n.children[0]))
    elif n.name == "VAL":
        return n.value


t = Tokenizer("5 * 3 + 2 - 4 * 8 / 2")
start = parse_expression(t)
print_node(start, 0)
print(eval_node(start))
