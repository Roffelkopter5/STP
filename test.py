from assembler.tokenizer import Tokenizer
from assembler.output import ErrorHandler, raise_error, TokenizationError

handler = ErrorHandler("aaaa")

raise_error(TokenizationError("Test", 0, 2))
