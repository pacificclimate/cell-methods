# cf-cell-methods

A [SLY](https://github.com/dabeaz/sly) parser for the content of the 
[`cell_methods`](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#cell-methods) 
attribute defined in CF Metadata Conventions.

Also will likely include a generator that translates this package's 
representation of `cell_methods` content into a valid `cell_methods` string.
Hence we don't call the package `cf-cell-methods-parser`.

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
cell_methods : simple_cell_methods | climatological_cell_methods
```

#### Simple statistics

Reference: 
[7.3. Cell Methods](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#cell-methods),
para. 1.

```
simple_cell_methods: 
    simple_cell_methods simple_cell_methods_item 
    | simple_cell_methods_item
```
```
simple_cell_methods_item : NAME COLON method opt_cell_portions opt_extra_info
```

#### Climatological statistics

Reference: 
[7.4. Climatological Statistics](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#climatological-statistics)

```
climatological_cell_methods : 
    climo_stats_methods opt_climo_stats_models_method
```
```
climo_stats_methods : climo_stats_yy | climo_stats_dd | climo_stats_ddy
```
```
climatological_stats_yy : 
    TIME COLON method WITHIN YEARS opt_non_standardized_extra_info
    TIME COLON method OVER YEARS opt_non_standardized_extra_info
```
```
climatological_stats_dd : 
    TIME COLON method WITHIN DAYS opt_non_standardized_extra_info
    TIME COLON method OVER DAYS opt_non_standardized_extra_info
```
```
climatological_stats_ddy : 
    TIME COLON method WITHIN DAYS opt_non_standardized_extra_info
    TIME COLON method OVER DAYS opt_non_standardized_extra_info
    TIME COLON method OVER YEARS opt_non_standardized_extra_info
```

We extend the CF Conventions here by allowing an optional statistic-over-models
method as well at the end of any climatological statistics.

```
opt_climo_stats_models_method = climo_stats_models_method | empty
```
```
climo_stats_models_method = MODELS COLON method opt_non_standardized_extra_info
```

#### Atomic methods

These are the core statistical operations performed on data.

All methods except `percentile` are prescribed by 
[CF Conventions, Appendix E: Cell Methods](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#appendix-cell-methods).

```
atomic_method : POINT | SUM | MAXIMUM | MAXIMUM_ABSOLUTE_VALUE
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

```
opt_cell_portions : cell_portions | empty
```
```
cell_portions : cell_portions_where opt_cell_portions_over
```
```
cell_portions_where : WHERE type 
```
```
opt_cell_portions_over : OVER type | empty
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

