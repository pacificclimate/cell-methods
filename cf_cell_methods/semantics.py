"""
Semantic checks on cell methods.
"""
from cf_cell_methods import parse


def parse_if_str(cell_methods):
    return parse(cell_methods) if isinstance(cell_methods, str) \
        else cell_methods


def make_equality_comparator(comparison):
    comparison = parse_if_str(comparison)
    return lambda cell_methods: parse_if_str(cell_methods) == comparison


# Hydrology cell method comparators

is_streamflow_raw = make_equality_comparator("time: mean within days")
is_streamflow_climatology = make_equality_comparator(
    "time: mean within days time: mean over days"
)
is_rp5_streamflow_single_model = make_equality_comparator(
    "time: mean within days time: mean over days"
)
is_rp5_streamflow_climatology_single_model = make_equality_comparator(
    "time: mean within days time: max over days time:mean over days"
)
is_rp5_streamflow_climatology_ensemble_mean = make_equality_comparator(
    "time: mean within days time: max over days time: mean over days "
    "models: mean"
)


def is_rp5_streamflow_ensemble_percentile(p, cell_methods):
    cell_methods = parse_if_str(cell_methods)
    return (
        len(cell_methods) == 4
        and is_rp5_streamflow_climatology_single_model(cell_methods[0:3])
        and cell_methods[4] == parse(f"models: percentile[{p}]")[0]
    )


# These comparators may or may not be useful to us and/or may be better
# reformulated with `match`. Kind of on hold here.

conventional_methods = {
    "num",
    "name",
    "point",
    "sum",
    "maximum",
    "maximum_absolute_value",
    "median",
    "mid_range",
    "minimum",
    "minimum_absolute_value",
    "mean",
    "mean_absolute_value",
    "mean_of_upper_decile",
    "mode",
    "range",
    "root_mean_square",
    "standard_deviation",
    "sum_of_squares",
    "variance",
}

extended_methods = {
    ("percentile", 1),
}


def is_conventional_1(cell_method):
    """
    Test if a cell_method is "conventional", which is to say does it conform
    to CF Conventions, specifically:
    - has a conventional method (e.g., "mean")

    We can't test more than this because it requires the larger context of
    the other cell_methods (for distinguishing climatological methods) or
    the NetCDF file (for validating axis names).

    Not much use, is this?
    """
    return (
        cell_method.method.name in conventional_methods
        and len(cell_method.method.params) == 0
    )


def is_extended_1(cell_method):
    return (
        is_conventional_1(cell_method)
        or cell_method.method.signature() in extended_methods
    )


def is_conventional_climatology(cell_methods):
    if not all(is_conventional_1(cm) for cm in cell_methods):
        return False

    if not all(cm.name == "time" for cm in cell_methods):
        return False

    within_over = tuple((cm.within, cm.over) for cm in cell_methods)
    if (within_over not in {
        (("years", None), (None, "years")),
        (("days", None), (None, "days")),
        (("days", None), (None, "days"), (None, "years")),
    }):
        return False

    return True


def is_conventional(cell_methods):
    # Check methods
    for cell_method in cell_methods:
        if not is_conventional_1(cell_method):
            return False

    # Check climatological cases
    if is_conventional_climatology(cell_methods):
        return True

    # Check non-climatological cases
    # - over clause if present always accompanied by where clause
    # - no within clause
    if not all(cm.over is None or cm.where is not None for cm in cell_methods):
        return False
    if not all(cm.within is None for cm in cell_methods):
        return False

    return True
