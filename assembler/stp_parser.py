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
    BINARY_OP = auto()
    UNARY_OP = auto()
    INSTR = auto()
    ARGS = auto()
    VALUE = auto()
    LABEL = auto()
    DIRECTIVE = auto()
    PREPROCESSOR = auto()


@dataclass
class Node:
    node_type: NodeType
    value: Any
    tokens: list[Token] = field(repr=False)
    children: list[Node] = field(repr=False, default_factory=list)


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
        signature = Signature([p.token_type for p in params])
        

    def parse_instruction(self):
        instr_token = self.tokenizer.get_next_token()
        instr_name = instr_token.value.upper()
        if instr_name in INSTRUCTION_SET:
            signatures = INSTRUCTION_SET[instr_name]
            index, args = self.select_signature(signatures)
            args_node = self.parse_args(args)
            return Node(NodeType.INSTR, signatures[index].memory_layout, [instr_token], [args_node])
        elif instr_name in self.macros:
            signatures = self.macros_sig[instr_name]
            index, args = self.select_signature(signatures)
            return self.resolve_macro(index, args)
        else:
            raise ParsingError("Unnkown Instruction!")

    def select_signature(self, signatures: list[Signature]):
        arguments = []
        while self.tokenizer.peek_next_token().token_type in TokenType.PARAM:
            arguments.append(self.tokenizer.get_next_token())
        nargs = len(arguments)
        possible = [len(s) == nargs for s in range(len(signatures))]
        for k, arg in enumerate(arguments):
            for i, sig in enumerate(signatures):
                if possible[i]:
                    if arg.token_type not in sig.param_types[k]:
                        possible[i] = False
            if arg in TokenType.EXPRESSION:
                # Consume all Tokens in Expression
                while self.tokenizer.peek_next_token().token_type in TokenType.EXPRESSION:
                    arguments.append(self.tokenizer.get_next_token())
        index = -1
        for i, p in enumerate(possible):
            if index != -1:
                raise ParsingError("Signature Overlap")
            if p:
               index = p 
        return index, arguments

    def parse_args(self, args: list[Token]):
        values = []
        for arg in args:
            t_type = arg.token_type
            if t_type in TokenType.EXPRESSION:
                self.parse_expression()

    def resolve_macro(self, index: int, args: list[Token]):
        raise NotImplementedError

    def body(self) -> list[Node]:
        return self.root.children

    def expect(self, token_type: TokenType):
        token = self.tokenizer.get_next_token()
        if token.token_type != token_type:
            raise ParsingError(f"Unexpected Token. Expected {token_type}")
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
