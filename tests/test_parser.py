import pytest
from cf_cell_methods.lexer import lexer
from cf_cell_methods.parser import parser
from cf_cell_methods.representation import (
    CellMethod, Method, ExtraInfo, SxiInterval,
)

@pytest.mark.parametrize(
    "data, expected",
    (
        (
            'time: mean',
            [CellMethod("time", Method("mean", None))]
        ),
        (
            'time: percentile[5]',
            [CellMethod("time", Method("percentile", (5,)))]
        ),
        (
            'time: mean where land',
            [CellMethod("time", Method("mean", None), where="land")]
        ),
        (
            'time: mean over years',
            [CellMethod("time", Method("mean", None), over="years")]
        ),
        (
            'time: mean where land over years',
            [CellMethod("time", Method("mean", None), where="land", over="years")]
        ),
        (
            'time: mean (interval: 1 day)',
            [
                CellMethod(
                    "time",
                    Method("mean", None),
                    extra_info=ExtraInfo(SxiInterval(1.0, "day"), None)
                )
            ]
        ),
        (
            'time: mean (frogs)',
            [
                CellMethod(
                    "time",
                    Method("mean", None),
                    extra_info=ExtraInfo(None, "frogs")
                )
            ]
        ),
        (
            'time: percentile[5] (interval: 1 day comment: frogs)',
            [
                CellMethod(
                    "time",
                    Method("percentile", (5,)),
                    extra_info=ExtraInfo(SxiInterval(1.0, "day"), "frogs")
                )
            ]
        ),
        (
            'time: mean lon: median lat: standard_deviation',
            [
                CellMethod("time", Method("mean", None)),
                CellMethod("lon", Method("median", None)),
                CellMethod("lat", Method("standard_deviation", None)),
            ]
        ),
    )
)
def test_parser(data, expected):
    result = parser.parse(lexer.tokenize(data))
    # for r, e in zip(result, expected):
    #     print(f"{r} | {e}")
    assert result == expected
