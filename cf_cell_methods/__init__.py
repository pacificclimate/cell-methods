from cf_cell_methods.lexer import lexer
from cf_cell_methods.parser import parser as token_parser


def parse(string):
    return token_parser.parse(lexer.tokenize(string))
