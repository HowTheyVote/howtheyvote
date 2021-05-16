import re
from bs4 import Tag
from typing import Optional
from typing import Dict, List


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

            for br_tag in cell_tag.select("BR"):
                br_tag.replace_with(" ")

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


def normalize_whitespace(string: str) -> str:
    string = string.replace("+", " + ")
    return re.sub(r"\s+", " ", string)


def extract_reference(string: Optional[str]) -> Optional[str]:
    if not string:
        return None

    reference_regex = r"(A|B|C|RC-B)\d+-\d{4}/\d{4}"
    match = re.search(reference_regex, string)

    return match.group(0) if match else None
