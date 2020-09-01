import json
from datetime import date
from enum import Enum
from dataclasses import is_dataclass, asdict
from typing import Any, Optional


class EPVotesEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, date):
            return obj.strftime(self.DATE_FORMAT)

        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, Enum):
            return obj.name

        if is_dataclass(obj):
            return asdict(obj)

        return super(EPVotesEncoder, self).default(obj)


def to_json(data: Any, indent: Optional[int] = None) -> str:
    return json.dumps(data, cls=EPVotesEncoder, indent=2)


def removeprefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix) :]

    return string[:]


def removesuffix(string: str, suffix: str) -> str:
    if string.endswith(suffix):
        return string[: -len(suffix)]

    return string[:]
