from enum import Enum, auto
from dataclasses import dataclass
import re


class TokenizationError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class TokenType(Enum):
    LABEL = auto()
    PREPROCESSOR = auto()
    DIRECTIVE = auto()
    IDENTIFIER = auto()
    REGISTER = auto()
    INT_LITERAL = auto()
    HEX_LITERAL = auto()
    BIN_LITERAL = auto()
    CHAR_LITERAL = auto()
    STRING_LITERAL = auto()
    COMMA = auto()
    OPERATOR = auto()


@dataclass
class Token:
    token_type: TokenType
    value: str
    line_nr: int = 0
    char_nr: int = 0


TOKEN_DEFINTIONS = {
    TokenType.LABEL: re.compile(r"^[a-z]\w*:", re.IGNORECASE),
    TokenType.PREPROCESSOR: re.compile(r"^@[a-z]\w*", re.IGNORECASE),
    TokenType.DIRECTIVE: re.compile(r"^\.[a-z]\w*", re.IGNORECASE),
    TokenType.IDENTIFIER: re.compile(r"[a-z]\w*", re.IGNORECASE),
    TokenType.REGISTER: re.compile(r"^r\d{1,2}"),
    TokenType.INT_LITERAL: re.compile(r"^\d+"),
    TokenType.HEX_LITERAL: re.compile(r"^0x[\dA-F]+", re.IGNORECASE),
    TokenType.BIN_LITERAL: re.compile(r"^0b[01]+", re.IGNORECASE),
    TokenType.CHAR_LITERAL: re.compile(r"'.*'"),
    TokenType.STRING_LITERAL: re.compile(r"\".*\""),
    TokenType.COMMA: re.compile(r"^,"),
    TokenType.OPERATOR: re.compile(r"^\+|-|\*|/|~|\||&"),
}
COMMENT_AND_WHITESPACE = re.compile(r"^\s*(#[^\n]*|\s+)")


class Tokenizer:
    def __init__(self, buffer: str) -> None:
        self.buffer = buffer.strip()
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
        while m := re.match(COMMENT_AND_WHITESPACE, self.buffer[self.pointer :]):
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
