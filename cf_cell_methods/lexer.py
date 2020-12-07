from sly import Lexer


class CfcmLexer(Lexer):
    tokens = {
        # Punctuation
        COLON, 
        LPAREN, 
        RPAREN,

        # Values
        NUM, 
        NAME,
        STRING,

        # Keywords
        POINT,
        SUM,
        MAXIMUM,
        MAXIMUM_ABSOLUTE_VALUE,
        MEDIAN,
        MID_RANGE,
        MINIMUM,
        MINIMUM_ABSOLUTE_VALUE,
        MEAN,
        MEAN_ABSOLUTE_VALUE,
        MEAN_OF_UPPER_DECILE,
        MODE,
        RANGE,
        ROOT_MEAN_SQUARE,
        STANDARD_DEVIATION,
        SUM_OF_SQUARES,
        VARIANCE,
        PERCENTILE,
        COMMENT,
        MODELS,
        WHERE,
        OVER,
        INTERVAL,
    }
    ignore = ' \t'

    # Tokens
    # TODO: Convert to literals declaration
    COLON = r':'
    LPAREN = r'\('
    RPAREN = r'\)'

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
    NAME['point'] = POINT
    NAME['sum'] = SUM
    NAME['maximum'] = MAXIMUM
    NAME['maximum_absolute_value'] = MAXIMUM_ABSOLUTE_VALUE
    NAME['median'] = MEDIAN
    NAME['mid_range'] = MID_RANGE
    NAME['minimum'] = MINIMUM
    NAME['minimum_absolute_value'] = MINIMUM_ABSOLUTE_VALUE
    NAME['mean'] = MEAN
    NAME['mean_absolute_value'] = MEAN_ABSOLUTE_VALUE
    NAME['mean_of_upper_decile'] = MEAN_OF_UPPER_DECILE
    NAME['mode'] = MODE
    NAME['range'] = RANGE
    NAME['root_mean_square'] = ROOT_MEAN_SQUARE
    NAME['standard_deviation'] = STANDARD_DEVIATION
    NAME['sum_of_squares'] = SUM_OF_SQUARES
    NAME['variance'] = VARIANCE
    NAME['percentile'] = PERCENTILE
    NAME['comment'] = COMMENT
    NAME['models'] = MODELS
    NAME['where'] = WHERE
    NAME['over'] = OVER
    NAME['interval'] = INTERVAL

    def error(self, t):
        print(f"Unexpected character '{t.value[0]}' at column {self.index}")
        self.index += 1

lexer = CfcmLexer()
