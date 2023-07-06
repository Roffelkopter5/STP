from __future__ import annotations
from typing import Any, DefaultDict
from collections import defaultdict
from enum import Enum, auto
from .tokenizer import Tokenizer, Token, TokenType
from dataclasses import dataclass, field


class ParsingError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class NodeType(Enum):
    ROOT = auto()
    INSTR = auto()
    LABEL = auto()
    EXPRESSION = auto()
    REGISTER = auto()
    IREGISTER = auto()


@dataclass
class Node:
    node_type: NodeType
    value: Any = None
    tokens: list[Token] | None = field(repr=False, default=None)
    children: list[Node] | None = field(repr=False, default=None)


@dataclass
class Signature:
    param_types: list[TokenType]
    param_count: int
    memory_layout: int = -1


INSTRUCTION_SET: dict[str, list[Signature]] = {
    "ADD": [Signature([TokenType.RPARAM, TokenType.RPARAM, TokenType.RPARAM], 3, 0)]
}
ARGUMENT_TOKENS: list[TokenType] = []

REGISTER_MAPPING: dict[str, int] = {"r1": 1, "r2": 2, "r3": 3}
IREGISTER_MAPPING: dict[str, int] = {}


class Parser:
    def __init__(self, buffer: str = ""):
        self.tokenizer = Tokenizer(buffer)
        self.root = Node(NodeType.ROOT, children=[])

        self.macros: DefaultDict[str, list[Signature]] = defaultdict(list)

    def parse(self):
        token = self.tokenizer.peek_next_token()
        node = None
        while token.token_type != TokenType.EOF:
            match token.token_type:
                case TokenType.DIRECTIVE:
                    node = self.parse_directive()
                case TokenType.LABEL:
                    self.tokenizer.get_next_token()
                    node = Node(NodeType.LABEL, token.value[:-1], [token])
                case TokenType.PREPROCESSOR:
                    node = self.parse_preprocessor()
                case TokenType.IDENTIFIER:
                    node = self.parse_instruction()
                case TokenType.EOL:
                    self.tokenizer.get_next_token()
                case _:
                    raise ParsingError("Unexpected Token")
            if isinstance(node, list):
                self.root.children.extend(node)
            elif node:
                self.root.children.append(node)
            token = self.tokenizer.peek_next_token()

    def parse_directive(self):
        pass

    def parse_preprocessor(self, token: Token):
        match token.value[1:].lower():
            case "macro":
                self.parse_macro(self)
            case "end":
                raise ParsingError("No prepocessor block to end")
            case _:
                raise ParsingError("Unknown preproccesor command")

    def parse_macro(self):
        name_token = self.expect(TokenType.IDENTIFIER)
        if name_token.value in INSTRUCTION_SET:
            raise ParsingError("Invalid macro name. Collides with instruction.")
        params = []
        while self.tokenizer.peek_next_token().token_type == TokenType.PARAM:
            params.append(self.tokenizer.get_next_token())

    def parse_instruction(self):
        instr_token = self.tokenizer.get_next_token()
        instr_name = instr_token.value.upper()
        if instr_name in INSTRUCTION_SET:
            signatures = INSTRUCTION_SET[instr_name]
            index, args = self.parse_args(signatures)
            return Node(
                NodeType.INSTR,
                signatures[index].memory_layout,
                [instr_token],
                args,
            )
        elif instr_name in self.macros:
            signatures = self.macros_sig[instr_name]
            index, args = self.parse_args(signatures)
            return self.resolve_macro(index, args)
        else:
            raise ParsingError(f"Unnkown Instruction! {instr_token}")

    def parse_args(self, signatures: list[Signature]):
        possible = [sig.param_count > 1 for sig in signatures]
        args = []
        count = sum(possible)
        index = 0
        while count > 0:
            token = self.tokenizer.peek_next_token()
            token_type = token.token_type
            if token_type in TokenType.IMMEDIATE | TokenType.OPEN_PARAN:
                args.append(self.consume_expression())
            elif token_type == TokenType.REGISTER:
                self.tokenizer.get_next_token()
                args.append(
                    Node(NodeType.REGISTER, REGISTER_MAPPING[token.value], [token])
                )
            elif token_type == TokenType.IREGISTER:
                self.tokenizer.get_next_token()
                args.append(
                    Node(NodeType.REGISTER, IREGISTER_MAPPING[token.value], [token])
                )
            else:
                break
            for i, sig in enumerate(signatures):
                if not possible[i]:
                    continue
                if index >= sig.param_count:
                    possible[i] = False
                    count -= 1
                    continue
                if token_type not in sig.param_types[index]:
                    possible[i] = False
                    count -= 1
                    continue
            index += 1
            self.expect(TokenType.COMMA | TokenType.EOF | TokenType.EOL)
        if count > 1:
            raise ParsingError("Unexcpected condition: Colliding signatures.")
        if count == 0:
            raise ParsingError("No signature matches the given arguments")
        sig_index = possible.index(True)
        return sig_index, args

    def consume_expression(self):
        expr = Node(NodeType.EXPRESSION)
        token = self.tokenizer.get_next_token()
        while True:
            token_type = token.token_type
            if token_type in TokenType.IMMEDIATE | TokenType.CLOSE_PARAN:
                token = self.tokenizer.peek_next_token()
                if token.token_type not in TokenType.OPERATOR | TokenType.CLOSE_PARAN:
                    break
            elif token_type in TokenType.OPERATOR | TokenType.OPEN_PARAN:
                token = self.expect(TokenType.OPEN_PARAN | TokenType.IMMEDIATE)
            else:
                raise ParsingError("Unexpected condition: Diffrent expression grammar")
            expr.tokens.append(token)
        return expr

    def resolve_macro(self, index: int, args: list[Token]):
        raise NotImplementedError

    def body(self) -> list[Node]:
        return self.root.children

    def expect(self, token_type: TokenType, error: str = "", peek: bool = False):
        if peek:
            token = self.tokenizer.peek_next_token()
        else:
            token = self.tokenizer.get_next_token()
        if token.token_type not in token_type:
            raise ParsingError(
                error.format(token=token)
                if error
                else f"Unexpected Token {token.token_type}. Expected {token_type}"
            )
        return token

    def print_node(self, n, level):
        print(f"{' ' * level}{'-' if n.children else ' '} {n}")
        if n.children:
            for child in n.children:
                self.print_node(child, level + 1)

    def print_ast(self):
        self.print_node(self.root, 0)
