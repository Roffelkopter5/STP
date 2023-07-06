from enum import Flag, auto
from dataclasses import dataclass
import re


class TokenizationError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)


class TokenType(Flag):
    DUMMY = auto()
    EOF = auto()
    EOL = auto()
    LABEL = auto()
    PREPROCESSOR = auto()
    DIRECTIVE = auto()
    IDENTIFIER = auto()
    REGISTER = auto()
    IREGISTER = auto()
    INT_LITERAL = auto()
    HEX_LITERAL = auto()
    BIN_LITERAL = auto()
    CHAR_LITERAL = auto()
    STRING_LITERAL = auto()
    COMMA = auto()
    OPERATOR = auto()
    OPEN_PARAN = auto()
    CLOSE_PARAN = auto()
    IMMEDIATE = INT_LITERAL | HEX_LITERAL | BIN_LITERAL | CHAR_LITERAL | IDENTIFIER
    VPARAM = IMMEDIATE
    RPARAM = REGISTER | DUMMY
    IRPARAM = IREGISTER | DUMMY
    XPARAM = VPARAM | RPARAM
    IXPARAM = VPARAM | IRPARAM
    PARAM = VPARAM | RPARAM | IRPARAM | XPARAM | IXPARAM


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
    TokenType.REGISTER: re.compile(r"^r\d{1,2}", re.IGNORECASE),
    TokenType.IDENTIFIER: re.compile(r"^[a-z]\w*", re.IGNORECASE),
    TokenType.HEX_LITERAL: re.compile(r"^0x[\dA-F]+", re.IGNORECASE),
    TokenType.BIN_LITERAL: re.compile(r"^0b[01]+", re.IGNORECASE),
    TokenType.INT_LITERAL: re.compile(r"^\d+"),
    TokenType.CHAR_LITERAL: re.compile(r"^'.*'"),
    TokenType.STRING_LITERAL: re.compile(r"^\".*\""),
    TokenType.COMMA: re.compile(r"^,"),
    TokenType.OPEN_PARAN: re.compile(r"^\("),
    TokenType.CLOSE_PARAN: re.compile(r"^\)"),
    TokenType.OPERATOR: re.compile(r"^\+|-|\*|/|~|\||&|%"),
}
COMMENT_AND_WHITESPACE = re.compile(r"^\s*(#.*|\s)")


class Tokenizer:
    def __init__(self, buffer: str) -> None:
        self.line_index = 0
        self.char_index = 0
        self.buffer = buffer.strip().split("\n")
        self.buff_len = len(self.buffer)
        if self.buff_len == 0:
            self.curr_token = Token(TokenType.EOF, "", self.line_index, self.char_index)
        self.curr_token = self.scan_token()

    def peek_next_token(self):
        return self.curr_token

    def get_next_token(self):
        current = self.curr_token
        if current.token_type != TokenType.EOF:
            self.scan_token()
        return current

    def scan_token(self):
        if self.line_index >= self.buff_len:
            self.curr_token = Token(
                TokenType.EOF,
                "",
                self.line_index - 1,
                len(self.buffer[self.line_index - 1]) - 1,
            )
            return self.curr_token
        line = self.buffer[self.line_index]
        if self.char_index >= len(line):
            self.curr_token = Token(TokenType.EOL, "", self.line_index, self.char_index)
            self.line_index += 1
            self.char_index = 0
            return self.curr_token
        if m := re.match(COMMENT_AND_WHITESPACE, line[self.char_index :]):
            self.char_index += m.end()
            return self.scan_token()
        for token_type, token_def in TOKEN_DEFINTIONS.items():
            if m := re.match(token_def, line[self.char_index :]):
                self.curr_token = Token(
                    token_type, m[0], self.line_index, self.char_index
                )
                self.char_index += m.end()
                return self.curr_token
        raise TokenizationError(
            f"Unknown Token at '{self.buffer[self.pointer:self.pointer+20]}'"
        )
