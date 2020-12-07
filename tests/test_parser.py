import pytest
from cf_cell_methods.lexer import lexer
from cf_cell_methods.parser import parser
from cf_cell_methods.representation import CellMethod

@pytest.mark.parametrize(
    "data, expected",
    (
        (
            'time: mean',
            [CellMethod("time", "mean")]
        ),
    )
)
def test_parser(data, expected):
    result = parser.parse(lexer.tokenize(data))
    for r, e in zip(result, expected):
        print(f"{r} | {e}")
    assert result == expected
