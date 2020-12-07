import pytest
from cf_cell_methods.lexer import lexer

@pytest.mark.parametrize(
    "data, expected",
    (
        (
            'foo: bar 123 456.789 point sum (extra info)',
            [
                ("NAME", "foo"),
                ("COLON", ":"),
                ("NAME", "bar"),
                ("NUM", 123),
                ("NUM", 456.789),
                ("NAME", "point"),
                ("NAME", "sum"),
                ("EXTRA_INFO", "extra info"),
            ]
        ),
    ),
)
def test_lexer(data, expected):
    toks = list(lexer.tokenize(data))
    # print(toks)
    assert [(tok.type, tok.value) for tok in toks] == expected
