from sly import Parser
from cf_cell_methods.lexer import CfcmLexer
from cf_cell_methods.representation import (
    CellMethod, Percentile, ExtraInfo, SxiInterval,
)


class CfcmParser(Parser):
    # Get the token list from the lexer (required)
    tokens = CfcmLexer.tokens

    # Grammar rules and actions

    #### Start symbol

    start = 'cell_methods'

    @_("cell_methods cell_method")
    def cell_methods(self, p):
        print(f"cell_methods: self: {self}")
        print(f"cell_methods: p: {p}")
        return p.cell_methods + [p.cell_method]

    @_("cell_method")
    def cell_methods(self, p):
        print(f"cell_methods: self: {self}")
        print(f"cell_methods: p: {p}")
        return [p.cell_method]

    #### Cell method

    @_("NAME COLON method opt_where_clause opt_over_clause opt_extra_info")
    def cell_method(self, p):
        return CellMethod(
            name=p.NAME,
            method=p.method,
            where=p.opt_where_clause,
            over=p.opt_over_clause,
            extra_info=p.opt_extra_info,
        )

    #### Atomic methods

    @_(
        "POINT",
        "SUM",
        "MAXIMUM",
        "MAXIMUM_ABSOLUTE_VALUE",
        "MEDIAN",
        "MID_RANGE",
        "MINIMUM",
        "MINIMUM_ABSOLUTE_VALUE",
        "MEAN",
        "MEAN_ABSOLUTE_VALUE",
        "MEAN_OF_UPPER_DECILE",
        "MODE",
        "RANGE",
        "ROOT_MEAN_SQUARE",
        "STANDARD_DEVIATION",
        "SUM_OF_SQUARES",
        "VARIANCE",     
    )
    def method(self, p):
        return p[0]

    @_("PERCENTILE LPAREN NUM RPAREN")
    def method(self, p):
        return Percentile(p.NUM)

    #### Statistics applying to portions of cells (`where`, `over`)

    # TODO: Could these ...
    @_("WHERE NAME")
    def opt_where_clause(self, p):
        return p.NAME

    @_("empty")
    def opt_where_clause(self, p):
        return None

    # TODO: ... be replaced by this? If so, way better.
    # @_("WHERE NAME", "empty")
    # def opt_where_clause(self, p):
    #     if p[0] == "where":
    #         return p.NAME
    #     return None

    @_("OVER NAME")
    def opt_over_clause(self, p):
        return p.NAME

    @_("empty")
    def opt_over_clause(self, p):
        return None

    #### Extra method information

    @_("extra_info")
    def opt_extra_info(self, p):
        return p.extra_info

    @_("empty")
    def opt_extra_info(self, p):
        return None

    @_("LPAREN extra_info_content RPAREN")
    def extra_info(self, p):
        return p.extra_info_content

    @_("standardized_extra_info_content")
    def extra_info_content(self, p):
        return ExtraInfo(p.standardized_extra_info_content, None)

    @_("non_standardized_extra_info_content")
    def extra_info_content(self, p):
        return ExtraInfo(None, p.non_standardized_extra_info_content)

    @_("combined_extra_info_content")
    def extra_info_content(self, p):
        return p.combined_extra_info_content

    @_("INTERVAL COLON value unit")
    def standardized_extra_info_content(self, p):
        return SxiInterval(p.value, p.unit)

    @_("STRING")
    def non_standardized_extra_info_content(self, p):
        return p.STRING

    @_(
        # NB: concatenation, not alternation
        "standardized_extra_info_content "
        "COMMENT COLON non_standardized_extra_info_content"
    )
    def combined_extra_info_content(self, p):
        return ExtraInfo(
            p.standardized_extra_info_content,
            p.non_standardized_extra_info_content
        )

    @_("NAME")
    def value(self, p):
        return p.name

    @_("NAME")
    def unit(self, p):
        return p.name

    #### Helper symbols

    @_("")
    def empty(self, p):
        print(f"empty: {p}")
        pass


parser = CfcmParser()