from sly import Lexer


class CfcmLexer(Lexer):
    tokens = {
        # Punctuation
        COMMA,
        COLON, 
        LBRACKET,
        RBRACKET,

        # Values
        NUM, 
        NAME,
        EXTRA_INFO,

        # Keywords
        COMMENT,
        MODELS,
        WHERE,
        OVER,
        INTERVAL,
    }
    ignore = ' \t'

    # Tokens

    # Punctuation
    COMMA = r','
    COLON = r':'
    LBRACKET = r'\['
    RBRACKET = r'\]'

    # Values
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    NUM = r'\d+(\.\d+)?'
    def NUM(self, t):
        t.value = float(t.value)
        return t

    # See comments to rule `extra_info`
    EXTRA_INFO = r'\([^)]*\)'
    def EXTRA_INFO(self, t):
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
