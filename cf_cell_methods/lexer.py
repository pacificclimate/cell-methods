from sly import Lexer


class CfcmLexer(Lexer):
    tokens = {
        # Punctuation
        COMMA,
        COLON, 
        LPAREN, 
        RPAREN,
        LBRACKET,
        RBRACKET,

        # Values
        NUM, 
        NAME,
        STRING,

        # Keywords
        COMMENT,
        MODELS,
        WHERE,
        OVER,
        INTERVAL,
    }
    ignore = ' \t'

    # Tokens
    # TODO: Convert to literals declaration?
    COMMA = r','
    COLON = r':'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    NUM = r'\d+(\.\d+)?'
    def NUM(self, t):
        t.value = float(t.value)
        return t

    STRING = r'"[^"]*"'
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    # Keywords (NAME special cases)
    NAME['comment'] = COMMENT
    NAME['models'] = MODELS
    NAME['where'] = WHERE
    NAME['over'] = OVER
    NAME['interval'] = INTERVAL

    def error(self, t):
        print(f"Unexpected character '{t.value[0]}' at column {self.index}")
        self.index += 1

lexer = CfcmLexer()
