import json
from datetime import date
from enum import Enum
from bs4 import Tag
from dataclasses import is_dataclass
from typing import Any, Optional, List, Dict
from .models import Vote, Voting


class EPVotesEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, date):
            return obj.strftime(self.DATE_FORMAT)

        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, Enum):
            return obj.name

        if isinstance(obj, Vote):
            return dict(obj.__dict__, formatted=obj.formatted)

        if isinstance(obj, Voting):
            return [obj.name, obj.position]

        if is_dataclass(obj):
            return obj.__dict__

        return super(EPVotesEncoder, self).default(obj)


def to_json(data: Any, indent: Optional[int] = None) -> str:
    return json.dumps(data, cls=EPVotesEncoder, indent=indent)


def removeprefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]

    return string[:]


def removesuffix(string: str, suffix: str) -> str:
    if string.endswith(suffix):
        return string[: -len(suffix)]

    return string[:]


Row = Dict[str, Optional[str]]
Rows = List[Row]


def normalize_table(table_tag: Tag) -> Rows:
    row_tags = table_tag.select("TR")
    rows: Rows = []
    current_rowspans: Dict[str, int] = {}

    for row_tag in row_tags:
        row = {}
        cell_tags = row_tag.select("TD")

        # Copy contents from cells beginning in a previous row
        for column_name, rowspan in current_rowspans.items():
            if rowspan > 0:
                row[column_name] = rows[-1][column_name]
                current_rowspans[column_name] -= 1

        # Set contents of cells beginning in current row
        offset = 0

        for cell_tag in cell_tags:
            column_number = int(cell_tag["COLNAME"].lower()[1:]) + offset
            column_name = "c" + str(column_number)
            row[column_name] = cell_tag.text.strip()

            # Update rowspan values in case cell spans multiple rows
            rowspan = int(cell_tag.get("ROWSPAN", "1"))
            current_rowspans[column_name] = rowspan - 1

            # Update colspan in case cell spans multiple columns
            offset += int(cell_tag.get("COLSPAN", 1)) - 1

        rows.append(row)

    # Use column headers as keys in subsequent rows
    header = rows[0]
    body = rows[1:]

    for index, row in enumerate(body):
        body[index] = {header[key] or key: value for key, value in row.items()}

    return body
