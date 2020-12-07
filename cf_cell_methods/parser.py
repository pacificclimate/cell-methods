import re
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

    # This is our workaround for the fact that the cell_methods grammar is
    # not quite context-free due to the format for "extra information." We treat
    # extra information like a quoted string, but the "quotes" are matching
    # parentheses. The string between the parentheses is then parsed separately.
    @_("EXTRA_INFO")
    def extra_info(self, p):
        # TODO: It would be better to parse this little sub-language with a real
        #   parser. regex FTW :-P
        match = re.match(
            r"(?P<interval>\s*interval:\s+(?P<value>\d+(\.\d+)?)\s+"
            r"(?P<unit>\w+)(\s+comment: )?)?"
            r"(?P<comment>.*)",
            p.EXTRA_INFO
        )
        standardized = (
            match.group('interval') and
            SxiInterval(float(match.group('value')), match.group('unit'))
        )
        non_standardized = match.group('comment') or None
        return ExtraInfo(standardized, non_standardized)

    # Helper symbols

    @_("")
    def empty(self, p):
        pass


parser = CfcmParser()
