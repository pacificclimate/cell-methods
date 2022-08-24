# cf-cell-methods

A [SLY](https://github.com/dabeaz/sly) parser for the content of the 
[`cell_methods`](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#cell-methods) 
attribute defined in CF Metadata Conventions.

## Purpose

The purpose of this package is to enable us to convert an arbitrary
`cell_methods` string into an easily processed, structured representation,
and to provide additional tools for processing 
(e.g., comparing representations).

Conversely, a representation is easy to convert back into
a correct `cell_methods` string because all representation classes
have defined `__str__` appropriately.

## Installation

```
pip install cf-cell-methods
```

## Usage

### Parse a cell_methods string

```
from cf_cell_methods import parse

representation = parse(cell_methods_string)
# `representation` is a list of `CellMethods` objects.
```

### Exact matching of cell methods

We can use `parse` to build a representation with which to compare for equality.
This makes exact matching easy.

(Yes, we could build regexes to do these matches, but this is easier,
more readable, and more maintainable.)

#### Simple case

This is also embodied in the method
`cf_cell_methods.semantics.is_streamflow_climatology`.

```python
from cf_cell_methods import parse

if (
    parse(cell_methods_string) 
    == parse("time: mean within days time: mean over days")
):
    # Yes it exactly matches
    pass
```

#### Case with variable part

This is also embodied in the method
`cf_cell_methods.semantics.is_rp5_streamflow_ensemble_percentile`.

```python
from cf_cell_methods import parse

p = 5

cell_methods = parse(cell_methods_string)
if (
    len(cell_methods) == 4
    # Fixed part
    and cell_methods[0:3] == 
        parse("time: mean within days time:max over days time: mean over days")
    # Variable part
    and cell_methods[4] == parse(f"models: percentile[{p}]")[0]
):
    # Yup!
    pass
```

For more examples, see 
module [semantics](cf_cell_methods/semantics.py).

### Partial matching of cell methods

I am contemplating several options for enabling partial matches, including:

- Partial matching by specifying a subset of object attribute values that
  are compared for equality.
  This is embodied at present in the `match` methods of representation classes.
  
- Extending the above by adding "matcher" objects that would enable the `match`
  methods to match on various more general criteria such as "any of", 
  or a regular expression.
  
- Partial matching between representation objects, specifying the attributes
  to compare. This might make it easier to construct objects to match against,
  but on the other hand such objects may have to include unused attributes
  to make them legal. That is a definite downside.
  
Any of these should wait until there are actual use cases.

## Other examples

See the [semantics](cf_cell_methods/semantics.py)
module for some examples of how to use this package to
match a cell methods string to a given pattern.


## Representation

The purpose of this package is to enable us to convert an arbitrary
`cell_methods` string into an easily processed, structured representation.

What does "structured representation" mean?

- It means a Python data structure, not a plain string, whose
   structure and content is suitable for processing programmatically,
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
(For example, in our extension of statistical methods to encompass percentiles,
we need methods with parametrizations so that we can express which percentile
it is.)

This suggests a relatively simple representation: A sequence (list or tuple)
of `CellMethod` objects, with appropriate subsidiary objects as needed to 
represent those of its attributes with compound values (e.g., `Method`.) See
module [representation](cf_cell_methods/representation.py).

## Semantics

The parser checks for syntactic correctness, but does not address meaning.
Semantics addresses meaning. The parsing of a cell methods string into a 
representation makes processing semantics much easier.

In our current use cases, "semantics" means two things:
- Does a given cell methods string match a pattern we are looking for?
- Is a given cell methods string semantically valid? 

There is much more here that can be done, but awaits some use cases to drive
it.

Just as one can construct
grammatically correct but nonsensical sentences in English 
(or buggy code in Python), it is possible to construct cell methods strings
that are (according to our somewhat forgiving parser) syntactically valid
but illegal according to the semantic constraints stated in the 
CF Conventions.

### Semantics: Climatological statistics cell methods

Reference: 
[7.4. Climatological Statistics](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#climatological-statistics)

For climatological statistics cell methods, the standard permits only one 
of 3 specific forms for cell methods. (See paragraph 5 and following of
[7.4. Climatological Statistics](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#climatological-statistics)
). Each of those forms combine `within` and `over` keywords in forms with
with specific meaning and application. 

**IMPORTANT**: The meaning of any instance of a climatological statistics 
`cell_methods` string cannot be understood fully without the context of the
climatology bounds for the dataset it applies to.

**NOTE**: It is also helpful to read the examples in Section 7.4 of the 
standard. They flesh out the abstract rules in a very informative way.

Strictly speaking, cell methods for climatological statistics are syntactically
distinguishable from other ("simple") cell methods. The distinction lies in
the use of the `within` and `over` keywords.

In this grammar we elide the syntactic distinction, using a considerably
simpler grammar, and instead treat the distinction as a semantic one. 
The semantic distinction, in the simpler grammar, is how the expressions
involving `within` and `over` are used. Once again, see Section 7.4.

This semantic distinction is far easier to implement and gives us just the right 
amount of flexibility for considered extensions to the CF Conventions.

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
cell_method : NAME COLON method clauses extra_info?
```
```
clauses : where_clause? over_clause? | within_clause?
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

#### Statistics applying to portions of cells (`where`, `over` clauses)

Reference:
[7.3.3. Statistics applying to portions of cells](http://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html#statistics-applying-portions).

See also 
[Semantics: Climatological statistics cell methods](#semantics-climatological-statistics-cell-methods)
for usage of the `over` clause.

```
where_clause : WHERE NAME
```
```
over_clause : OVER NAME
```

#### Climatological statistics (`within` clause)

Reference:
[Semantics: Climatological statistics cell methods](#semantics-climatological-statistics-cell-methods).

```
within_clause : WITHIN NAME
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


### Extensions

#### Methods

We extend the CF Conventions by allowing an optional statistic-over-models
method as well at the end of climatological statistics.
Again, this is a semantic not a syntactic constraint.

## Releasing

To create a versioned release:

1. Increment `version` in `setup.py`.
1. Summarize the changes from the last version in `NEWS.md`
1. Commit these changes, then tag the release.
1. Push to the repo.

  ```bash
git add setup.py NEWS.md
git commit -m"Bump to version x.x.x"
git tag -a -m"x.x.x" x.x.x
git push --follow-tags
  ```
