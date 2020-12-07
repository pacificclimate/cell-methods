# cf-cell-methods

A [SLY](https://github.com/dabeaz/sly) parser for the content of the 
[`cell_methods`](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#cell-methods) 
attribute defined in CF Metadata Conventions.

The parser converts a `cell_methods` string into a Python representation of
the content (or throws a parsing error).

The parsed representation of a `cell_methods` string includes the ability
to convert it into a valid `cell_methods` string.

## Installation

```
pip install cf-cell-methods
```

## Usage

```
from cf_cell_methods.lexer import lexer
from cf_cell_methods.parser import lexer

...

rep = parser.parse(lexer.tokenize(cell_methods_string))
```

The usage above could be packaged up into a single method.


## Purpose and realization

The purpose of this package is to enable us to convert an arbitrary
`cell_methods` into an easily processed, structured representation.
(Conversely, such a representation would be easy to convert back into
a correct `cell_methods` string.)

What does "structured representation" mean?

- It means a Python data structure, not a plain string, whose
   structure and content is suitable for processing it programatically,
   a.k.a. "easily processed."

What does "easily processed" mean?

1. As simple as possible while still explicitly representing the full 
   meaning of the string.
1. Suited to our purposes, which are to query the value for meaning.
   (This statement hides a lot of details!)   
1. Therefore an AST directly reflecting the grammar is unlikely to be 
   either simple or suitable.
   
If we consider the form of a `cell_methods` string, we see a sequence of
individual cell methods. Each individual cell method contains some mandatory
and some optional information. Some of these values are themselves complex.
(For example, in our extension statistical methods to encompass percentiles,
we need methods with parametrizations so that we can express which percentile
it is.)

This suggests a relatively simple representation: A sequence (list or tuple)
of `CellMethod` objects, with appropriate subsidiary objects as needed to 
represent those of its attributes with compound values (e.g., `Method`.) See
module [representation](cf_cell_methods/representation.py).

## Implementation planning

### Parsing tool

We've chosen SLY to implement the parser.

#### Why SLY?

SLY is a Python implementation of the lex and yacc tools commonly used to 
write parsers and compilers. SLY is an updated version of PLY, whose
[web page](http://www.dabeaz.com/ply/index.html) states

> PLY is no longer maintained as pip-installable package. Although no new 
> features are planned, it continues to be maintained and modernized. 
> If you want to use the latest version, you need to check it out from the 
> PLY GitHub page. If you are looking for a parser generator with a more 
> modern flavor look at the SLY Project.

This -- and SLY's relative elegance, concision, and tranparency -- 
argues for SLY as the foundational tool here. SLY isn't well documented,
but [PLY is](http://www.dabeaz.com/ply/ply.html). SLY is so similar that 
I expect PLY's documentation to be sufficient. 
This [video](https://www.youtube.com/watch?v=zJ9z6Ge-vXs) of a PyCon
presentation by David Beazley, the author of SLY and PLY, is instructive.

## Parsing

This section presents the information needed to construct a parser for
`cell_methods`.

### Tokens

These define the lexical tokens of the `cell_methods` language.
Their definition in the [lexer](cf_cell_methods/lexer.py) is clear.

The only item that might be confusing is the treatment of the entire
"extra information" content as single token, EXTRA_INFO, a string-like 
token whose content is delimited by matching parentheses.
See the note in the [parser](cf_cell_methods/parser.py) for why this is done.
(I suspect I may be wrong that extra info cannot be treated as a CFL, but
this solved the problem much faster.)

### Grammar

The grammar for `cell_methods` is presented here in Extended BNF. A little
work expands it into the plain BNF accepted by SLY, yacc, etc.

The rules tend to be in top-down order, but are not strictly so.

#### Start symbol

```
cell_methods : cell_method*
```

#### Cell method

Reference: 
[7.3. Cell Methods](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#cell-methods),
para. 1.

```
cell_method : NAME COLON method where_clause? over_clause? extra_info?
```

#### Methods

These are the core statistical operations performed on data.

All methods except `percentile` are prescribed by 
[CF Conventions, Appendix E: Cell Methods](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#appendix-cell-methods).

```
method : NAME params?
```

Note parameter list is enclosed in square brackets to disambiguate it from
the possible parenthesis-delimited extra info portion that could immediately 
follow an unparametrized method. Since this is our own extension, we get to
choose.

```
params: LBRACKET param_list RBRACKET
```
```
param_list: param_list COMMA param | param
```
```
param : NUM
```

#### Statistics applying to portions of cells (`where`, `over`)

Reference:
[7.3.3. Statistics applying to portions of cells](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#statistics-applying-portions).

See also 
[Climatological statistics cell methods](#climatological-statistics-cell-methods)
for usage of the `over` clause.

```
where_clause : WHERE NAME
```
```
over_clause : OVER NAME
```

#### Extra method information

Reference:
[7.3.2. Recording the spacing of the original data and other information](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#recording-spacing-original-data).

```
extra_info : EXTRA_INFO
```

The content of the `EXTRA_INFO` token is parsed separately inside the
`extra_info` method. This avoids the problem that the definition of
extra information in the Conventions appears to make it not quite strictly
a CFG.


#### Helper symbols

```
empty :
```

## Semantics

### Climatological statistics cell methods

Reference: 
[7.4. Climatological Statistics](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#climatological-statistics)

Strictly speaking, cell methods for climatological statistics are syntactically
distinguishable from other ("simple") cell methods. The distinction lies in 
the use of the `over` keyword. In simple cell methods, an `over` subexpression
must be preceded by a `where` subexpression. In climatological cell methods,
only the `over` subexpression can appear. 
Furthermore, the acceptable values in the `over` subexpression are in distinct
classes for each (much limited in the climatological case). 
However, I think that one could construct a case where a simple cell method 
`over` values looked like climatological cell method `over` values, 
specifically by using the terms `years` and `days` very idiosyncratically.
It may be possible however that there are in fact two separate vocabularies
for each case (simple: spatial; climatological: temporal).

*However*, as the above discussion shows, this syntactic distinction is quite
subtle. In this grammar we elide the syntactic distinction, using a considerably
simpler grammar, and instead treat the distinction as a semantic one. 
The semantic distinction, in the simpler grammar, is on the presence of 
a `where` subexpression and the value in the `over` subexpression.

This semantic distinctin is far easier to implement and gives us just the right 
amount of flexibility for considered extensions to the CF Conventions.

### Extensions

#### Methods

We extend the CF Conventions by allowing an optional statistic-over-models
method as well at the end of climatological statistics.
Again, this is a semantic not a syntactic constraint.

