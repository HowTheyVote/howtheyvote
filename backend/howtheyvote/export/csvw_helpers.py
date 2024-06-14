import csv
import datetime
import pathlib
from collections.abc import Generator
from contextlib import contextmanager
from types import NoneType, UnionType
from typing import Any, Generic, Self, TypeVar, cast, get_args, TypedDict, NotRequired

from ..helpers import get_attribute_docstrings
from ..json import json_dumps

T = TypeVar("T")


class Table(Generic[T]):
    def __init__(
        self,
        row_type: type[T],
        outdir: pathlib.Path,
        name: str,
        primary_key: str | list[str],
    ):
        self.row_type = row_type
        self.outdir = outdir
        self.name = name
        self.primary_key = primary_key

        self.columns = list(self.row_type.__annotations__)

        self.table_file = self.outdir.joinpath(f"{self.name}.csv")
        self.meta_file = self.outdir.joinpath(f"{self.name}.csv-metadata.json")

    @contextmanager
    def open(self) -> Generator[Self, None, None]:
        with (
            self.table_file.open("w+") as table_handle,
            self.meta_file.open("w+") as meta_handle,
        ):
            self.table_handle = table_handle
            self.meta_handle = meta_handle

            self.writer = csv.DictWriter(self.table_handle, self.columns)
            self.write_header()
            self.write_metadata()

            yield self

    def write_header(self) -> None:
        self.writer.writeheader()

    def write_row(self, row: T) -> None:
        self.writer.writerow(cast(dict[str, Any], row))

    def write_metadata(self) -> None:
        metadata = {
            "@context": "http://www.w3.org/ns/csvw",
            "url": self.get_filename(),
            "dc:created": datetime.datetime.now(datetime.UTC),
            "dc:license": {
                "@id": "https://opendatacommons.org/licenses/odbl/1-0",
            },
            "dc:creator": {"@id": "https://howtheyvote.eu"},
            "dc:publisher": {"@id": "https://howtheyvote.eu"},
            "tableSchema": get_schema(self.row_type),
            "primaryKey": self.primary_key,
            "dialect": {
                "header": True,
            },
        }

        self.meta_handle.write(json_dumps(metadata, indent=2))


Column = TypedDict(
    "Column",
    {
        "datatype": str,
        "required": bool,
        "dc:description": NotRequired[str],
    },
)


class NamedColumn(Column):
    name: str


class TableSchema(TypedDict):
    columns: list[NamedColumn]


def get_schema(row_type: type) -> TableSchema:
    columns: list[NamedColumn] = []
    docstrings = get_attribute_docstrings(row_type)

    for column, col_type in row_type.__annotations__.items():
        definition: NamedColumn = {
            "name": column,
            **get_column_definition(col_type),
        }

        if docstrings.get(column):
            definition["dc:description"] = docstrings[column]

        columns.append(definition)

    return {"columns": columns}


def get_column_definition(col_type: type) -> Column:
    if col_type == bool:
        return {
            "datatype": "boolean",
            "required": True,
        }

    if col_type == int:
        return {
            "datatype": "integer",
            "required": True,
        }

    if col_type == float:
        return {
            "datatype": "decimal",
            "required": True,
        }

    if col_type == str:
        return {
            "datatype": "string",
            "required": True,
        }

    if col_type == datetime.date:
        return {
            "datatype": "date",
            "required": True,
        }

    if col_type == datetime.datetime:
        return {
            "datatype": "dateTime",
            "required": True,
        }

    if isinstance(col_type, UnionType):
        type_args = get_args(col_type)

        # This currently doesn't handle union types of more than two non-None types
        # because we haven't had a need for it so far.
        if len(type_args) == 2 and NoneType in type_args:
            other_type = next(arg for arg in type_args if arg is not NoneType)
            definition = get_column_definition(other_type)
            definition["required"] = False
            return definition

    raise Exception(f"Could not get column definition for {col_type}")
