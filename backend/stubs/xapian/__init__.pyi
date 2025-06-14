"""
This file contains type stubs for the Xapian Python bindings. I've generated a draft
using the stubgen tool that is included in mypy:

```
stubgen -m xapian
```

I've then removed all incomplete types that we do not use at the moment and manually updated
the incomplete types we use. If we extend our usage of the Python bindings in the future, we
may need to add addition types to this file.

The Python bindings mirror the C++ API for the most part, but there are some exceptions to
follow Python conventions.

For the C++ API reference see: https://xapian.org/docs/apidoc/html/annotated.html
For the Python-specific APIs see: https://github.com/xapian/xapian/blob/master/xapian-bindings/python3/extra.i
"""

from collections.abc import Iterator
from typing import overload

DB_CREATE_OR_OPEN: int

class Document:
    def __init__(self) -> None: ...
    def add_value(self, slot: int, value: str) -> None: ...
    def add_boolean_term(self, term: str) -> None: ...

class Query:
    OP_AND: int
    OP_OR: int
    OP_AND_NOT: int
    OP_XOR: int
    OP_AND_MAYBE: int
    OP_FILTER: int
    OP_NEAR: int
    OP_PHRASE: int
    OP_VALUE_RANGE: int
    OP_SCALE_WEIGHT: int
    OP_ELITE_SET: int
    OP_VALUE_GE: int
    OP_VALUE_LE: int
    OP_SYNONYM: int
    OP_MAX: int
    OP_WILDCARD: int
    OP_INVALID: int
    MatchAll: Query
    MatchNothing: Query
    def empty(self) -> bool: ...
    @overload
    def __init__(self, term: str, wqf: int = ..., pos: int = ...) -> None: ...
    @overload
    def __init__(self, op: int, query: Query, factor: float) -> None: ...
    @overload
    def __init__(self, op: int, a: Query, b: Query) -> None: ...
    @overload
    def __init__(self, source: PostingSource) -> None: ...

class TermGenerator:
    def __init__(self) -> None: ...
    FLAG_SPELLING: int
    FLAG_NGRAMS: int
    FLAG_CJK_NGRAM: int
    STEM_NONE: int
    STEM_SOME: int
    STEM_ALL: int
    STEM_ALL_Z: int
    STEM_SOME_FULL_POS: int
    STOP_NONE: int
    STOP_ALL: int
    STOP_STEMMED: int
    def set_stopper(self, stopper: Stopper) -> None: ...
    def set_stopper_strategy(self, strategy: int) -> None: ...
    def set_document(self, doc: Document) -> None: ...
    def set_database(self, db: WritableDatabase) -> None: ...
    def set_flags(self, toggle: int, mask: int = ...) -> None: ...
    def index_text(self, text: str, wdf_inc: int = ..., prefix: str = ...) -> None: ...
    def increase_termpos(self, delta: int = ...) -> None: ...

class MSet:
    def get_matches_estimated(self) -> int: ...
    def size(self) -> int: ...
    def __iter__(self) -> Iterator[MSetItem]: ...

class MSetItem:
    docid: int

class Enquire:
    def __init__(self, database: Database) -> None: ...
    def set_query(self, query: Query, qlen: int = ...) -> None: ...
    def set_weighting_scheme(self, weight: Weight) -> None: ...
    def set_sort_by_value(self, sort_key: int, reverse: bool) -> None: ...
    def set_sort_by_relevance_then_value(self, sort_key: int, reverse: bool) -> None: ...
    def get_mset(self, first: int, maxitems: int) -> MSet: ...

class Stopper:
    def __init__(self) -> None: ...

class SimpleStopper(Stopper):
    def __init__(self, path: str) -> None: ...

class QueryParser:
    def __init__(self) -> None: ...
    FLAG_BOOLEAN: int
    FLAG_BOOLEAN_ANY_CASE: int
    FLAG_CJK_NGRAM: int
    FLAG_DEFAULT: int
    FLAG_LOVEHATE: int
    FLAG_NGRAMS: int
    FLAG_NO_POSITIONS: int
    FLAG_PARTIAL: int
    FLAG_PHRASE: int
    FLAG_PURE_NOTE: int
    FLAG_SPELLING_CORRECTION: int
    FLAG_SYNONYM: int
    FLAG_WILDCARD: int
    def parse_query(self, query_string: str, flags: int = ..., prefix: str = ...) -> Query: ...
    def set_stopper(self, stopper: Stopper) -> None: ...
    def set_database(self, db: Database) -> None: ...
    def set_default_op(self, op: int) -> None: ...

def sortable_serialise(value: float) -> str: ...
def sortable_unserialise(serialised: str) -> float: ...

class Weight:
    pass

class BM25Weight(Weight):
    def __init__(
        self,
        k1: float,
        k2: float,
        k3: float,
        b: float,
        min_normlen: float,
    ) -> None: ...

class PostingSource:
    def __init__(self) -> None: ...

class ValuePostingSource(PostingSource):
    def __init__(self, slot: int) -> None: ...
    def get_value(self) -> str: ...

class ValueWeightPostingSource(ValuePostingSource):
    def __init__(self, slot: int) -> None: ...
    def get_weight(self) -> float: ...

class Database:
    def __init__(self, path: str, flags: int = ...) -> None: ...
    def close(self) -> None: ...

class WritableDatabase(Database):
    def __init__(self, path: str, flags: int = ..., block_size: int = ...) -> None: ...
    def replace_document(self, did: int, document: Document) -> None: ...
