from __future__ import annotations
from typing import Any, DefaultDict
from collections import defaultdict
from enum import Enum, auto
from tokenizer import Tokenizer, Token, TokenType
from dataclasses import dataclass, field


class ParsingError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class NodeType(Enum):
    ROOT = auto()
    INSTR = auto()
    LABEL = auto()
    EXPRESSION = auto()


@dataclass
class Node:
    node_type: NodeType
    value: Any = None
    tokens: list[Token] | None = field(repr=False, default=None)
    children: list[Node] | None = field(repr=False, default=None)


@dataclass
class Signature:
    param_types: list[TokenType]
    memory_layout: int = -1


@dataclass
class InstructionDef:
    name: str
    aliases: tuple[str] = None
    signatures: tuple[Signature] | Signature

    def isName(self, name: str) -> bool:
        return name == self.name or name in self.aliases


INSTRUCTION_SET: dict[str, list[Signature]]
ARGUMENT_TOKENS: list[TokenType]


class Parser:
    def __init__(self, *, path: str = "", buffer: str = ""):
        if path != "":
            with open(path, "r") as f:
                buffer = f.read()
        self.tokenizer = Tokenizer(buffer)
        self.root = Node(NodeType.ROOT, None)

        self.macros: DefaultDict[str, list[Signature]] = defaultdict(list)

    def parse(self):
        token = self.tokenizer.peek_next_token()
        while token:
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
                case _:
                    raise ParsingError("Unexpected Token")
            if isinstance(node, list):
                self.root.children.extend(node)
            else:
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
            index, args = self.select_signature(signatures)
            # FIXME
            args_node = self.parse_args(args)
            return Node(
                NodeType.INSTR,
                signatures[index].memory_layout,
                [instr_token],
                [args_node],
            )
        elif instr_name in self.macros:
            signatures = self.macros_sig[instr_name]
            index, args = self.select_signature(signatures)
            return self.resolve_macro(index, args)
        else:
            raise ParsingError("Unnkown Instruction!")

    def select_signature(self, signatures: list[Signature]):
        # TODO: Select a signature
        pass

    def consume_expression(self):
        expr = Node(NodeType.EXPRESSION)
        token = self.expect(TokenType.IMMEDIATE | TokenType.CLOSE_PARAN)
        while True:
            token_type = token.token_type
            if token_type in TokenType.IMMEDIATE | TokenType.CLOSE_PARAN:
                token = self.tokenizer.peek_next_token()
                if token not in TokenType.OPERATOR | TokenType.CLOSE_PARAN:
                    break
            elif token_type in TokenType.OPERATOR | TokenType.OPEN_PARAN:
                token = self.expect(TokenType.OPEN_PARAN | TokenType.IMMEDIATE)
            else:
                raise ParsingError("Unexpected condition. Report issue to ...")
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
                else f"Unexpected Token. Expected {token_type}"
            )
        return token

    def print_node(self, n, level):
        print(f"{' ' * level}{'-' if n.children else ' '} {n}")
        if n.children:
            for child in n.children:
                self.print_node(child, level + 1)

    def print_ast(self):
        self.print_node(self.root, 0)


p = Parser(buffer="ADD")
p.parse()
