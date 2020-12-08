import pytest
from cf_cell_methods.representation import (
    eq,
    _match,
    CellMethods,
    CellMethod,
    ExtraInfo,
    SxiInterval,
    Method,
)


class Thing:
    """Class for testing `eq`"""

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


@pytest.mark.parametrize(
    "a, b, attrs, expected",
    (
        (Thing(1, 2, 3), Thing(1, 2, 3), "x", True),
        (Thing(1, 2, 3), Thing(1, 2, 3), "x, y", True),
        (Thing(1, 2, 3), Thing(1, 2, 3), "x, y, z", True),
        (Thing(1, 2, 3), Thing(1, 2, 4), "x", True),
        (Thing(1, 2, 3), Thing(1, 2, 4), "x, y", True),
        (Thing(1, 2, 3), Thing(1, 2, 4), "x, y, z", False),
    ),
)
def test_eq(a, b, attrs, expected):
    assert eq(a, b, attrs) is expected


@pytest.mark.parametrize(
    "a, b, equal",
    (
        (Method("mean", None), Method("mean", None), True),
        (Method("median", None), Method("mean", None), False),
        (SxiInterval("1", "year"), SxiInterval("1", "year"), True),
        (SxiInterval("2", "year"), SxiInterval("1", "year"), False),
        (SxiInterval("1", "day"), SxiInterval("1", "year"), False),
        (
            ExtraInfo(SxiInterval("1", "year"), "foo"),
            ExtraInfo(SxiInterval("1", "year"), "foo"),
            True,
        ),
        (
            ExtraInfo(SxiInterval("1", "year"), "foo"),
            ExtraInfo(SxiInterval("2", "year"), "foo"),
            False,
        ),
        (
            ExtraInfo(SxiInterval("1", "year"), "foo"),
            ExtraInfo(SxiInterval("1", "year"), "bar"),
            False,
        ),
        (CellMethod("time", "mean"), CellMethod("time", "mean"), True),
        (CellMethod("time", "median"), CellMethod("time", "mean"), False),
        (
            CellMethod("time", "mean", where="foo"),
            CellMethod("time", "mean", where="foo"),
            True,
        ),
        (
            CellMethod("time", "mean", where="foo"),
            CellMethod("time", "mean", where="bar"),
            False,
        ),
        (
            CellMethod("time", "mean", over="foo"),
            CellMethod("time", "mean", over="foo"),
            True,
        ),
        (
            CellMethod("time", "mean", over="foo"),
            CellMethod("time", "mean", over="bar"),
            False,
        ),
        (
            CellMethod(
                "time",
                "mean",
                extra_info=ExtraInfo(SxiInterval("1", "year"), "foo"),
            ),
            CellMethod(
                "time",
                "mean",
                extra_info=ExtraInfo(SxiInterval("1", "year"), "foo"),
            ),
            True,
        ),
        (
            CellMethod(
                "time",
                "mean",
                extra_info=ExtraInfo(SxiInterval("1", "year"), "foo"),
            ),
            CellMethod(
                "time",
                "mean",
                extra_info=ExtraInfo(SxiInterval("2", "year"), "foo"),
            ),
            False,
        ),
        (
            [
                CellMethod(
                    "time",
                    "mean",
                    extra_info=ExtraInfo(SxiInterval("1", "year"), "foo"),
                )
            ],
            [
                CellMethod(
                    "time",
                    "mean",
                    extra_info=ExtraInfo(SxiInterval("1", "year"), "foo"),
                )
            ],
            True,
        ),
    ),
)
def test__eq__(a, b, equal):
    assert (a == b) is equal


@pytest.mark.parametrize(
    "data, expected",
    (
        (Method("mean", None), "mean"),
        (Method("percentile", (5,)), "percentile[5]"),
        (Method("gronk", (5, 6)), "gronk[5,6]"),
        (SxiInterval("1", "year"), "interval: 1 year"),
        (ExtraInfo(None, None), ""),
        (ExtraInfo(SxiInterval("1", "year"), None), "(interval: 1 year)"),
        (ExtraInfo(None, "this is a comment"), "(this is a comment)"),
        (
            ExtraInfo(SxiInterval("1", "year"), "this is a comment"),
            "(interval: 1 year comment: this is a comment)",
        ),
        (CellMethod("time", "mean"), "time: mean"),
        (CellMethod("time", "mean", where="land"), "time: mean where land"),
        (CellMethod("time", "mean", over="years"), "time: mean over years"),
        (
            CellMethod("time", "mean", where="land", over="years"),
            "time: mean where land over years",
        ),
        (CellMethod("time", "mean", within="days"), "time: mean within days"),
        (
            CellMethod(
                "time",
                "mean",
                extra_info=ExtraInfo(SxiInterval("1", "year"), "wow"),
            ),
            "time: mean (interval: 1 year comment: wow)",
        ),
        (
            CellMethods([
                CellMethod("time", "mean"),
                CellMethod("area", "standard_deviation", where="land"),
            ]),
            "time: mean area: standard_deviation where land"
        )
    ),
)
def test__str__(data, expected):
    assert str(data) == expected


class Thang:
    def __init__(self,a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def match(self, **kwargs):
        return _match(self, kwargs)


@pytest.mark.parametrize(
    "obj, what, expected",
    (
        # Atomic match values
        (Thing(1, 2, 3), {"x": 1}, True),
        (Thing(1, 2, 3), {"x": 99}, False),
        (Thing(None, 2, 3), {"x": None}, True),
        (Thing(None, 2, 3), {"x": 1}, False),
        (Thing(1, 2, 3), {"x": 1, "y": 2}, True),
        (Thing(1, 2, 3), {"x": 1, "y": 99}, False),
        # Compound match values, not None
        (
            Thing(1, 2, Thang(5, 6, 7)),
            {"x": 1, "y": 2, "z": {"a": 5, "b": 6}},
            True,
        ),
        (
            Thing(1, 2, Thang(8, 9, 10)),
            {"x": 1, "y": 2, "z": {"a": 5, "b": 99}},
            False,
        ),
        # Compound match values of None
        (
            Thing(1, 2, None),
            {"x": 1, "y": 2, "z": {"a": 5, "b": 6}},
            False,
        ),
        (
            Thing(1, 2, None),
            {"x": 1, "y": 2, "z": None},
            True,
        ),
    )
)
def test__match(obj, what, expected):
    assert _match(obj, what) is expected
