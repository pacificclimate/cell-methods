import pytest
from cf_cell_methods import parse
from cf_cell_methods.pcex_helpers import final_operation

@pytest.mark.parametrize(
    "cell_method_str, expected",
    (
        ("time: mean within years time: median over years", "median"),
        ("unspecified", None),
        ("time: max within days time: mean over days", "mean"),
        ("time: mean (interval: 20minutes)", "mean"),
        ("time: sum within days time: maximum within months", "maximum"),
        ("time: minimum within days time: count within years where < 0 C", None),
        ("time: mean within days time: maximum over days models: percentile[5]", "percentile"),
        ("area: mean", "mean")
    )
)
def test_final_operation(cell_method_str, expected):
    assert final_operation(cell_method_str) == expected
