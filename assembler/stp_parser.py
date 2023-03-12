from __future__ import annotations
from .tokenizer import Tokenizer, Token, TokenType
from dataclasses import dataclass, field


class ParsingError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


@dataclass
class Node:
    token: Token
    children: list[Node] = field(repr=False)


A0_INSTRUCTIONS = ["HLT", "NOP"]
A1_INSTRUCTIONS = ["JMP", "JZE", "JNZ"]
A3_INSTRUCTIONS = [
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
]


class Parser:
    def __init__(self, path: str):
        with open(path, "r") as f:
            buffer = f.read()
        self.tokenizer = Tokenizer(buffer)
        self.root = Node(None, [])

    def parse(self):
        while t := self.tokenizer.get_next_token():
            if t.token_type == TokenType.IDENTIFIER:
                self.root.children.append(self.parse_instruction(t))
            elif t.token_type == TokenType.DIRECTIVE:
                print("TODO (Directive)")
            elif t.token_type == TokenType.LABEL:
                self.root.children.append(Node(t, []))
            else:
                raise ParsingError(
                    f"Invalid token! Excpected 'IDENTIFIER' or 'LABEL' got '{t.token_type.name}'"
                )

    # TODO: Better Layout/Signature System. It's a total mess
    def parse_instruction(self, t: Token):
        if t.value in A3_INSTRUCTIONS:
            args = self.parse_A3()
        elif t.value in A1_INSTRUCTIONS:
            args = self.parse_A1()
        elif t.value in A0_INSTRUCTIONS:
            args = [Node(Token(TokenType.SIGNATURE, ["L3"]), [])]
        else:
            raise ParsingError(f"Unknown instruction '{t.value}'")
        t.token_type = TokenType.INSTRUCTION
        return Node(t, args)

    def parse_A1(self):
        sig = Token(TokenType.SIGNATURE, ["L3", "I16"])
        return [Node(sig, []), self.parse_int()]

    # TODO: just no, neeads cleaning up
    def parse_A3(self):
        args = []
        sig = Token(TokenType.SIGNATURE, [])
        n = self.parse_register()
        args.append(n)
        sig.value.append("RD")
        self.parse_comma()
        n = self.parse_register()
        args.append(n)
        sig.value.append("RS1")
        self.parse_comma()
        s, n = self.parse_register_or_int()
        args.append(n)
        sig.value.append(s)
        if s == "I8":
            sig.value.insert(0, "L1")
        else:
            sig.value.insert(0, "L0")
        args.insert(0, Node(sig, []))
        return args

    def parse_comma(self):
        t = self.tokenizer.get_next_token()
        if t.token_type != TokenType.COMMA:
            raise ParsingError("Missing ',' between arguments")

    def parse_register(self, current=False):
        t = self.tokenizer.get_next_token()
        if t.token_type != TokenType.REGISTER:
            raise ParsingError(
                f"Worng arguments! Expected 'REGISTER' got '{t.token_type.name}'"
            )
        return Node(t, None)

    # TODO: Does it need to be a separate method
    def parse_register_or_int(self):
        t = self.tokenizer.get_next_token()
        if t.token_type == TokenType.REGISTER:
            return "RS2", Node(t, None)
        elif t.token_type == TokenType.INTEGER or t.token_type == TokenType.IDENTIFIER:
            return "I8", Node(t, None)
        else:
            raise ParsingError(
                f"Wrong arguments! Expected 'REGISTER' or 'INTEGER' got '{t.token_type.name}'"
            )

    def parse_int(self):
        t = self.tokenizer.get_next_token()
        if t.token_type != TokenType.INTEGER and t.token_type != TokenType.IDENTIFIER:
            raise ParsingError(
                f"Wrong arguments! Expected 'INTEGER' got '{t.token_type.name}'"
            )
        return Node(t, None)

    def body(self) -> list[Node]:
        return self.root.children

    def print_node(self, n, level):
        print(f"{' ' * level}{'-' if n.children else ' '} {n}")
        if n.children:
            for child in n.children:
                self.print_node(child, level + 1)

    def print_ast(self):
        self.print_node(self.root, 0)
