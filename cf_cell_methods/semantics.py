"""
Semantic checks on cell methods (which are necessarily syntactically valid if
they can be represented `CellMethod`.
"""

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
    return cell_method.method.name in conventional_methods


def is_extended_1(cell_method):
    return (
        cell_method.method.name in conventional_methods
        or (cell_method.method.name, len(cell_method.method.params)) in
        extended_methods
    )


def is_conventional(cell_methods):
    # Check methods
    for cell_method in cell_methods:
        if not is_conventional_1(cell_method):
            return False

    # Check climatological cases
    # - name = time for all
    # - one of (within years, over years), (within days, over days),
    #   (within days, over days, over years)
    if all(cm.name == "time" for cm in cell_methods):
        sig = tuple((cm.within, cm.over) for cm in cell_methods)
        if (sig in {
            (("years", None), (None, "years")),
            (("days", None), (None, "days")),
            (("days", None), (None, "days"), (None, "years")),
        }):
            return True

    # Check non-climatological cases
    # - over if present always preceded by where
    if all(cm.over is None or cm.where is not None for cm in cell_methods):
        return True

    # Nope
    return False
