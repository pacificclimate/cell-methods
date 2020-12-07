import pytest
from cf_cell_methods.lexer import lexer
from cf_cell_methods.parser import parser
from cf_cell_methods.representation import (
    CellMethod, ExtraInfo, SxiInterval,
)

@pytest.mark.parametrize(
    "data, expected",
    (
        (
            'time: mean',
            [CellMethod("time", "mean")]
        ),
        (
            'time: mean where land',
            [CellMethod("time", "mean", where="land")]
        ),
        (
            'time: mean over years',
            [CellMethod("time", "mean", over="years")]
        ),
        (
            'time: mean where land over years',
            [CellMethod("time", "mean", where="land", over="years")]
        ),
        (
            'time: mean (interval: 1 day)',
            [
                CellMethod(
                    "time",
                    "mean",
                    extra_info=ExtraInfo(SxiInterval(1, "day"), None)
                )
            ]
        ),
        (
            'time: mean ("frogs")',
            [
                CellMethod(
                    "time",
                    "mean",
                    extra_info=ExtraInfo(None, "frogs")
                )
            ]
        ),
        (
            'time: mean (interval: 1 day comment: "frogs")',
            [
                CellMethod(
                    "time",
                    "mean",
                    extra_info=ExtraInfo(SxiInterval(1, "day"), "frogs")
                )
            ]
        ),
        (
            'time: mean lon: median lat: standard_deviation',
            [
                CellMethod("time", "mean"),
                CellMethod("lon", "median"),
                CellMethod("lat", "standard_deviation"),
            ]
        ),
    )
)
def test_parser(data, expected):
    result = parser.parse(lexer.tokenize(data))
    # for r, e in zip(result, expected):
    #     print(f"{r} | {e}")
    assert result == expected
