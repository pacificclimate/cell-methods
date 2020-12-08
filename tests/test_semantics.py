import pytest
from cf_cell_methods import parse
from cf_cell_methods.semantics import (
    is_streamflow_raw,
    is_streamflow_climatology,
    is_conventional_1,
    is_extended_1,
    is_conventional_climatology,
    is_conventional,
)


@pytest.mark.parametrize(
    "cell_method_str, expected",
    (
        ("time: mean within days", True),
        ("lon: mean within days", False),  # Meaningless, but ...
        ("time: mean within years", False),
    ),
)
def test_is_streamflow_raw(cell_method_str, expected):
    assert is_streamflow_raw(cell_method_str) is expected


@pytest.mark.parametrize(
    "cell_method_str, expected",
    (
        ("time: mean within days", False),
        ("time: mean within days time: mean over days", True),
    ),
)
def test_is_streamflow_climatology(cell_method_str, expected):
    assert is_streamflow_climatology(cell_method_str) is expected


@pytest.mark.parametrize(
    "cell_method_str, conventional, extended",
    (
        ("time: mean", True, True),
        ("time: mean[3]", False, False),
        ("time: unconventional", False, False),
        ("time: percentile[3]", False, True),
    ),
)
def test_single(cell_method_str, conventional, extended):
    cell_methods = parse(cell_method_str)
    assert is_conventional_1(cell_methods[0]) is conventional
    assert is_extended_1(cell_methods[0]) is extended


@pytest.mark.parametrize(
    "cell_method_str, expected",
    (
        # The three valid cases
        ("time: mean within years time: median over years", True),
        ("time: mean within days time: median over days", True),
        (
            "time: mean within days time: median over days time: "
            "standard_deviation over years",
            True,
        ),
        # Some invalid cases
        ("time: mean", False),
        ("time: mean within days time: median over years", False),
        ("time: mean within years time: median over days", False),
        (
            "time: mean within days time: median over days time: "
            "standard_deviation over centuries",
            False,
        ),
    ),
)
def test_is_conventional_climatology(cell_method_str, expected):
    cell_methods = parse(cell_method_str)
    assert is_conventional_climatology(cell_methods) is expected


@pytest.mark.parametrize(
    "cell_method_str, expected",
    (
        # Three conventional climatological cases
        ("time: mean within years time: median over years", True),
        ("time: mean within days time: median over days", True),
        (
            "time: mean within days time: median over days time: "
            "standard_deviation over years",
            True,
        ),
        # Some conventional non-climo cases
        ("time: mean", True),
        ("area: mean where land", True),
        ("area: mean where sea_ice over sea", True),
        # Some conventional erroneous cases
        ("area: mean within years", False),
        # ("", True),
    ),
)
def test_is_conventional(cell_method_str, expected):
    cell_methods = parse(cell_method_str)
    assert is_conventional(cell_methods) is expected
