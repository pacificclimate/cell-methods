import pytest
from cf_cell_methods import parse
import time


@pytest.mark.parametrize(
    "string, n",
    (
        ("time: mean", 10000),
        (
            "time: mean within days time:max over days "
            "time: mean over days models: percentile[5]",
            10000,
        ),
    )
)
def test_parser_speed(string, n):
    start_time = time.time()
    for i in range(n):
        parse(string)
    elapsed_time = time.time() - start_time
    print(
        f"\nelapsed time: {elapsed_time}; time per parse: {elapsed_time / n}"
    )
