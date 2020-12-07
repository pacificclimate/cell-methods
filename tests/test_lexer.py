import pytest
from cf_cell_methods.lexer import lexer

@pytest.mark.parametrize(
    "data, expected",
    (
        (
            'foo: bar 123 456.789 point sum " an example string"',
            [
                ("NAME", "foo"),
                ("COLON", ":"),
                ("NAME", "bar"),
                ("NUM", 123),
                ("NUM", 456.789),
                ("NAME", "point"),
                ("NAME", "sum"),
                ("STRING", " an example string"),
            ]
        ),
    ),
)
def test_lexer(data, expected):
    toks = list(lexer.tokenize(data))
    # print(toks)
    assert [(tok.type, tok.value) for tok in toks] == expected
