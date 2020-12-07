from sly import Parser
from cf_cell_methods.lexer import CfcmLexer
from cf_cell_methods.representation import (
    CellMethod, Method, ExtraInfo, SxiInterval,
)


class CfcmParser(Parser):
    # Get the token list from the lexer (required)
    tokens = CfcmLexer.tokens

    # Grammar rules and actions
    start = 'cell_methods'

    # Start symbol

    @_("cell_methods cell_method")
    def cell_methods(self, p):
        return p.cell_methods + [p.cell_method]

    @_("cell_method")
    def cell_methods(self, p):
        return [p.cell_method]

    # Cell method

    @_("NAME COLON method opt_where_clause opt_over_clause opt_extra_info")
    def cell_method(self, p):
        return CellMethod(
            name=p.NAME,
            method=p.method,
            where=p.opt_where_clause,
            over=p.opt_over_clause,
            extra_info=p.opt_extra_info,
        )

    # Method (with optional params)

    @_("NAME opt_params")
    def method(self, p):
        return Method(p.NAME, p.opt_params)

    @_("params")
    def opt_params(self, p):
        return p.params

    @_("empty")
    def opt_params(self, p):
        return None

    @_("LBRACKET param_list RBRACKET")
    def params(self, p):
        return p.param_list

    @_("param_list COMMA param")
    def param_list(self, p):
        return p.param_list + (p.param,)

    @_("param")
    def param_list(self, p):
        return (p.param,)

    @_("NUM")
    def param(self, p):
        return p.NUM

    # Statistics applying to portions of cells (`where`, `over`)

    @_("WHERE NAME")
    def opt_where_clause(self, p):
        return p.NAME

    @_("empty")
    def opt_where_clause(self, p):
        return None

    @_("OVER NAME")
    def opt_over_clause(self, p):
        return p.NAME

    @_("empty")
    def opt_over_clause(self, p):
        return None

    # Extra method information

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

    @_("NUM")
    def value(self, p):
        return p.NUM

    @_("NAME")
    def unit(self, p):
        return p.NAME

    # Helper symbols

    @_("")
    def empty(self, p):
        pass


parser = CfcmParser()
