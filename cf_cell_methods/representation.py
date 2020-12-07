import re


def eq(a, b, attrs):
    """Compare two objects on named attributes"""
    for attr in re.split(r"\s*,\s*", attrs):
        left, right = (getattr(obj, attr) for obj in (a, b))
        if left != right:
            # print(f"eq False on attr '{attr}': {left!r} != {right!r}")
            return False
    return True


def strict_join(seq, sep=" "):
    """Join a sequence of objects "strictly", which means ignoring None
    values."""
    return sep.join(s for s in seq if s is not None)


class CellMethod:
    def __init__(self, name, method, where=None, over=None, extra_info=None):
        self.name = name
        self.method = method
        self.where = where
        self.over = over
        self.extra_info = extra_info

    def __eq__(*args):
        return eq(*args, "name, method, where, over, extra_info")

    def __str__(self):
        return strict_join(
            (
                f"{self.name}: {self.method}",
                self.where and f"where {self.where}",
                self.over and f"over {self.over}",
                self.extra_info and f"{self.extra_info}",
            )
        )


class ExtraInfo:
    def __init__(self, standardized, non_standardized):
        self.standardized = standardized
        self.non_standardized = non_standardized

    def __eq__(*args):
        return eq(*args, "standardized, non_standardized")

    def __str__(self):
        if self.standardized is None and self.non_standardized is None:
            # This actually should never occur
            return ""
        return (
            f"("
            f"{self.standardized or ''}"
            f"{' comment: ' if self.standardized and self.non_standardized else ''}"
            f"{self.non_standardized or ''}"
            f")"
        )


class StandardizedExtraInfo:
    pass


class SxiInterval(StandardizedExtraInfo):
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def __eq__(*args):
        return eq(*args, "value, unit")

    def __str__(self):
        return f"interval: {self.value} {self.unit}"


class Method:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def __eq__(*args):
        return eq(*args, "name, params")

    def __str__(self):
        params = (
            f"[{','.join(str(p) for p in self.params)}]"
            if self.params is not None else ""
        )
        return f"{self.name}{params}"

