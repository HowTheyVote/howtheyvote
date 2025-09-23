import ast
import hashlib
import inspect
import itertools
import re
from collections.abc import Iterable, Iterator, Mapping
from textwrap import dedent
from typing import Any, TypedDict, cast
from urllib.parse import urljoin

from . import config
from .models import DocumentType, ProcedureType

REFERENCE_REGEX = re.compile(
    r"(?P<type>A|B|C|RC-B)"
    + r"(?P<term>\d+)-"
    + r"(?P<number>\d{4})\/"
    + r"(?P<year>\d{4})"
    + r"(?:\/rev\d*)?",
    flags=re.IGNORECASE,
)

PROCEDURE_REFERENCE_REGEX = re.compile(
    r"(?P<year>\d{4})\/" + r"(?P<number>\d{4}[A-Z]?)" + r"\((?P<type>[A-Z]{3})\)",
    flags=re.IGNORECASE,
)

TEXTS_ADOPTED_REFERENCE_REGEX = re.compile(
    r"P(?P<term>\d+)" + r"_TA\((?P<year>\d{4})\)" + r"(?P<number>\d{4})",
    flags=re.IGNORECASE,
)


class Reference(TypedDict):
    type: DocumentType
    term: int
    number: int
    year: int


class ProcedureReference(TypedDict):
    type: ProcedureType
    number: str
    year: int


class TextsAdoptedReference(TypedDict):
    term: int
    number: int
    year: int


def parse_reference(reference: str) -> Reference:
    match = re.fullmatch(REFERENCE_REGEX, reference.upper())

    if not match:
        raise ValueError(f"Invalid reference: {reference}")

    type_code = cast(str, match.group("type"))

    if type_code == "RC-B":
        type_code = "RC"

    type_ = DocumentType[type_code]
    term = int(match.group("term"))
    number = int(match.group("number"))
    year = int(match.group("year"))

    return Reference(type=type_, term=term, number=number, year=year)


def parse_procedure_reference(procedure_reference: str) -> ProcedureReference:
    match = re.fullmatch(PROCEDURE_REFERENCE_REGEX, procedure_reference.upper())

    if not match:
        raise ValueError(f"Invalid procedure reference: {procedure_reference}")

    try:
        type_code = cast(str, match.group("type"))
        type_ = ProcedureType[type_code]
    except KeyError:
        raise ValueError(f"Invalid procedure type {type_code}") from None

    number = cast(str, match.group("number"))
    year = int(match.group("year"))

    return ProcedureReference(type=type_, number=number, year=year)


def parse_texts_adopted_reference(texts_adopted_reference: str) -> TextsAdoptedReference:
    match = re.fullmatch(TEXTS_ADOPTED_REFERENCE_REGEX, texts_adopted_reference.upper())

    if not match:
        raise ValueError(f"Invalid texts adopted reference: {texts_adopted_reference}")

    term = int(match.group("term"))
    number = int(match.group("number"))
    year = int(match.group("year"))

    return TextsAdoptedReference(term=term, number=number, year=year)


def make_key(*parts: str) -> str:
    digest = hashlib.sha1()

    for part in parts:
        digest.update(part.encode("utf-8"))

    return digest.hexdigest()


def chunks[T](iterable: Iterable[T], size: int) -> Iterator[Iterator[T]]:
    iterator = iter(iterable)

    for first in iterator:
        yield itertools.chain([first], itertools.islice(iterator, size - 1))


def frontend_url(path: str) -> str:
    return urljoin(config.FRONTEND_PUBLIC_URL, path)


def flatten_dict(data: Mapping[Any, Any], key_prefix: str = "") -> dict[Any, Any]:
    # Using `Mapping` type due to https://github.com/python/mypy/issues/4976

    flattened: dict[Any, Any] = {}

    for key, value in data.items():
        if key_prefix:
            key = f"{key_prefix}.{key}"

        if isinstance(value, Mapping):
            flattened.update(**flatten_dict(value, key_prefix=key))
        else:
            flattened[key] = value

    return flattened


def subset_dict(data: Mapping[Any, Any], keys: Iterable[Any]) -> Mapping[Any, Any]:
    if not isinstance(keys, set):
        keys = set(keys)

    return {k: v for k, v in data.items() if k in keys}


def get_class_ast(type_: type) -> ast.ClassDef:
    source = dedent(inspect.getsource(type_))
    tree = ast.parse(source)
    return cast(ast.ClassDef, tree.body[0])


def get_attribute_docstrings(type_: type) -> dict[str, str]:
    """Python doesn't expose docstrings for class attributes at runtime. This method
    parses the source code for the given class into an AST, then tries to find docstrings
    immediately following a class attribute annotation. It returns a mapping from attribute
    names to docstrings."""
    class_def = get_class_ast(type_)

    docstrings: dict[str, str] = {}
    prev_annotation = None

    for stmt in class_def.body:
        if isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name):
                prev_annotation = str(stmt.target.id)
                continue

        if isinstance(stmt, ast.Expr):
            if isinstance(stmt.value, ast.Constant):
                if prev_annotation:
                    docstrings[prev_annotation] = inspect.cleandoc(str(stmt.value.value))

        prev_annotation = None

    return docstrings


def get_normalized_docstring(type_: type) -> str:
    """Returns the docstring with leading whitespace removed."""

    docstring = type_.__doc__ or ""
    docstring = inspect.cleandoc(docstring)
    docstring = docstring.strip()

    # Remove single line breaks, but keep double line breaks
    docstring = re.sub(r"(?<!\n)\n(?!\n)", " ", docstring, flags=re.MULTILINE)

    return docstring
