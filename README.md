# cf-cell-methods

A [SLY](https://github.com/dabeaz/sly) parser for the content of the 
[`cell_methods`](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#cell-methods) 
attribute defined in CF Metadata Conventions.

Also will likely include a generator that translates this package's 
representation of `cell_methods` content into a valid `cell_methods` string.
Hence we don't call the package `cf-cell-methods-parser`.

## Implementation planning

### Purpose of parser

The purpose of this parser is to enable us to convert an arbitrary
`cell_methods` into an easily processed, structured representation.
(Conversely, such a representation would be easy to convert back into
a correct `cell_methods` string.)

What does "structured represenation" mean?

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
   
Let's take a shot at some kind of data structure. 
We'll try to keep the grammar symbol names and the class names consistent.
(This is a sort of UML-ish, sort of Python-ish representation of the data
structure.)

```
class CellMethods:
    methods : list(CellMethod)

class CellMethod:
    name: string
    method: string
    where: string (type) | None
    over: string (type) | None
    standardized_extra_info: StandardizedExtraInfo | None
    non_standardized_extra_info: string | None

class StandardizedExtraInfo
    type : 'interval' # only valid value at present
    value: string
    unit: string
```

## Notes

### Why SLY?

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

These define the lexical tokens of the `cell_methods` language as
regular expressions coded in Python. These can be incorporated directly into
a SLY Lexer.

#### Basic tokens

```
COLON = r':'
LPAREN = r'\('
RPAREN = r'\)'
NUM = r'[0-9]+(.[0-9]+)'
NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
```

#### Keyword tokens

These are the for the most part the keywords that can appear in the
`method` part of a `cell_method`. For reference see 
[CF Conventions, Appendix E: Cell Methods](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#appendix-cell-methods).
We've extended the CF Conventions list with the following custom items:

- `percentile`, which is the name of a parametrized method that yields
   percentile values; e.g., `percentile(5)` for 5th percentile.

```
POINT = r'point'
SUM = r'sum'
MAXIMUM = r'maximum'
MAXIMUM_ABSOLUTE_VALUE = r'maximum_absolute_value'
MEDIAN = r'median'
MID_RANGE = r'mid_range'
MINIMUM = r'minimum'
MINIMUM_ABSOLUTE_VALUE = r'minimum_absolute_value'
MEAN = r'mean' 
MEAN_ABSOLUTE_VALUE = r'mean_absolute_value'
MEAN_OF_UPPER_DECILE = r'mean_of_upper_decile'
MODE = r'mode'
RANGE = r'range' 
ROOT_MEAN_SQUARE = r'root_mean_square'
STANDARD_DEVIATION = r'standard_deviation'
SUM_OF_SQUARES = r'sum_of_squares'
VARIANCE = r'variance' 
PERCENTILE = r'percentile'
COMMENT = r'comment'
MODELS = r'models'
```

### Grammar

The grammar for `cell_methods` is presented here in the standard `yacc` form,
which is directly usable in constructing a SLY Parser.

The rules tend to be in top-down order, but are not strictly so.

#### Start symbol

```
cell_methods : cell_methods cell_method | cell_method
```

#### Cell method

Reference: 
[7.3. Cell Methods](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#cell-methods),
para. 1.

```
cell_method : NAME COLON method opt_where_clause opt_over_clause opt_extra_info
```

#### Atomic methods

These are the core statistical operations performed on data.

All methods except `percentile` are prescribed by 
[CF Conventions, Appendix E: Cell Methods](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#appendix-cell-methods).

```
method : POINT | SUM | MAXIMUM | MAXIMUM_ABSOLUTE_VALUE
    | MEDIAN | MID_RANGE | MINIMUM | MINIMUM_ABSOLUTE_VALUE | MEAN 
    | MEAN_ABSOLUTE_VALUE | MEAN_OF_UPPER_DECILE | MODE | RANGE 
    | ROOT_MEAN_SQUARE | STANDARD_DEVIATION | SUM_OF_SQUARES | VARIANCE 
    | percentile
```

```
percentile : PERCENTILE LPAREN NUM RPAREN
```

#### Statistics applying to portions of cells (`where`, `over`)

Reference:
[7.3.3. Statistics applying to portions of cells](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#statistics-applying-portions).

See also 
[Climatological statistics cell methods](#climatological-statistics-cell-methods)
for usage of the `over` clause.

```
opt_where_clause : WHERE type | empty
```
```
opt_over_clause : OVER type | empty
```
```
type : NAME
```

#### Extra method information

Reference:
[7.3.2. Recording the spacing of the original data and other information](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#recording-spacing-original-data).

```
opt_extra_info = extra_info | empty
```
```
extra_info : LPAREN extra_info_content RPAREN
```

```
opt_non_standardized_extra_info = non_standardized_extra_info | empty
```
```
non_standardized_extra_info : LPAREN non_standardized_extra_info_content RPAREN
```

```
extra_info_content : 
    standardized_extra_info_content 
    | non_standardized_extra_info_content
    | combined_extra_info_content
```
```
standardized_extra_info_content : INTERVAL COLON value unit
```

Definition of `non_standardized_extra_info_content` needs some refinement.
```
non_standardized_extra_info_content : <any string>
```

```
combined_extra_info_content : 
    standardized_extra_info_content 
    COMMENT COLON non_standardized_extra_info_content
```

#### Helper symbols

```
empty :
```

#### Climatological statistics cell methods

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

##### Extensions

We extend the CF Conventions by allowing an optional statistic-over-models
method as well at the end of climatological statistics.
Again, this is a semantic not a syntactic constraint.

