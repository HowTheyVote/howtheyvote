import dataclasses
import datetime
import enum
import json
from typing import Any

from flask.json.provider import DefaultJSONProvider


class JSONEncoder(json.JSONEncoder):
    """A JSON encoder that handles additional built-in types such as dates, sets, enums."""

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, datetime.datetime):
            return o.isoformat()

        if isinstance(o, enum.Enum):
            return o.value

        if isinstance(o, set):
            return sorted(o)

        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)

        return json.JSONEncoder.default(self, o)


def json_loads(string: str | bytes) -> Any:
    return json.loads(string)


def json_dumps(obj: Any, indent: int | None = None) -> Any:
    return JSONEncoder(indent=indent).encode(obj)


class JSONProvider(DefaultJSONProvider):
    def dumps(self, obj: Any, **kwargs: Any) -> Any:
        return json_dumps(obj)
