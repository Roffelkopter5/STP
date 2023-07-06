from __future__ import annotations
import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tokenizer import Token


class ErrorCode(IntEnum):
    TOKENIZATION = 100
    PARSING = 200
    COMPILING = 300
    INTERNAL = 400


VERBOSE_ERROR_NAMES: dict[int, str] = {
    ErrorCode.TOKENIZATION: "TokenizationError",
    ErrorCode.PARSING: "ParsingError",
    ErrorCode.COMPILING: "CompilationError",
    ErrorCode.INTERNAL: "InternalError",
}

_error_logger: logging.Logger = None
_buffer: list[str] = None


@dataclass
class STPError:
    msg: str
    code: ErrorCode = ErrorCode.INTERNAL
    token: Token = None
    data: dict = None
    line: int = -1
    char: int = -1


def TokenizationError(msg: str, line: int, char: int):
    return STPError(code=ErrorCode.TOKENIZATION, msg=msg, line=line, char=char)


class ErrorHandler:
    singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls.singleton:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def __init__(self, buffer: str):
        self.logger = logging.getLogger("error")
        error_stream = logging.StreamHandler()
        error_stream.setFormatter(
            logging.Formatter(
                fmt="\x1b[31m[%(errcode)d] %(errname)s: %(message)s\n\x1b[39;2m----- Traceback: '%(file)s' | Ln:%(ln)d Col:%(col)d -----\x1b[22m\n->\t%(line)s\n  \t\x1b[31m%(errline)s\x1b[39m",
                defaults={
                    "errcode": 400,
                    "errname": "InternalError",
                    "file": "dummy.stp",
                    "ln": 10,
                    "col": 3,
                    "line": "Hello World!",
                    "errline": " " * 6 + "~~~~~~",
                },
            )
        )
        self.logger.addHandler(error_stream)
        self.logger.setLevel(logging.ERROR)
        self.buffer = buffer.strip().split("\n")
        self.value = 4

    def raise_error(self, error: STPError):
        line = self.buffer[error.line]
        errline = " " * error.char + "~" * (
            len(error.token.value) if error.token else 1
        )
        self.logger.error(
            error.msg,
            extra={
                "errcode": error.code,
                "errname": VERBOSE_ERROR_NAMES[error.code],
                "line": line,
                "errline": errline,
                "ln": error.line,
                "col": error.char,
            },
        )


def raise_error(error: STPError):
    ErrorHandler.singleton.raise_error(error)
