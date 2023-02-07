from enum import Enum, auto
from dataclasses import dataclass
import re


class TokenizationError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class TokenType(Enum):
    INSTRUCTION = auto()
    REGISTER = auto()
    INTEGER = auto()
    COMMA = auto()
    LABEL = auto()
    MACRO = auto()
    DIRECTIVE = auto()
    IDENTIFIER = auto()
    SIGNATURE = auto()


@dataclass
class Token:
    token_type: TokenType
    value: str


TOKEN_DEFINTIONS = {
    TokenType.LABEL: re.compile(r"^[A-Z]+:"),
    TokenType.DIRECTIVE: re.compile(r"^\.[A-Z]+"),
    TokenType.IDENTIFIER: re.compile(r"[A-Z]+\b"),
    TokenType.REGISTER: re.compile(r"^R\d{1,2}"),
    TokenType.INTEGER: re.compile(r"^\d+"),
    TokenType.COMMA: re.compile(r"^,"),
}
COMMENT = re.compile(r"^\s*(#[^\n]*|\s+)")


class Tokenizer:
    def __init__(self, buffer: str) -> None:
        self.buffer = buffer.strip().upper()
        self.pointer = 0
        self.buff_len = len(self.buffer)
        self.curr_token = None

    def get_current_token(self):
        return self.curr_token

    def get_next_token(self):
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
