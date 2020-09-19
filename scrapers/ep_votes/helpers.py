import json
from datetime import date
from enum import Enum
from dataclasses import is_dataclass
from typing import Any, Optional
from .models import Voting


class EPVotesEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, date):
            return obj.strftime(self.DATE_FORMAT)

        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, Enum):
            return obj.name

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
