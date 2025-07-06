import dataclasses
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Self

from .json import json_dumps, json_loads

DATA_DIR = Path(__file__).resolve().parent / "data"


class DeserializableDataclass:
    @classmethod
    def from_dict(cls, data: dict[Any, Any]) -> Self:
        return cls(**data)


class DataclassContainer[T: DeserializableDataclass]:
    """A convenience class to write and load dataclasses from a JSON file and retrieve
    individual dataclass instances by key."""

    def __init__(self, dataclass: type[T], file_path: Path | str, key_attr: str):
        self.dataclass = dataclass
        self.file_path = Path(file_path)
        self.key_attr = key_attr
        self.index: dict[str, T] = {}

    def load(self) -> None:
        """Load data from file."""
        text = self.file_path.read_text()
        records = json_loads(text)

        for record in records:
            self.add(self.dataclass.from_dict(record))

    def save(self) -> None:
        """Save data to file."""
        records = [dataclasses.asdict(r) for r in self.index.values()]  # type: ignore
        records = sorted(records, key=lambda r: r[self.key_attr])
        text = json_dumps(records, indent=2)
        self.file_path.write_text(text)

    def add(self, record: T) -> None:
        """Add an individual record."""
        key = getattr(record, self.key_attr)

        if not isinstance(key, str):
            raise TypeError("Key value must be a string")

        self.index[key.lower()] = record

    def get(self, key: str | None) -> T | None:
        """Get a record by key."""
        if not key:
            return None

        return self.index.get(key.lower())

    def __iter__(self) -> Iterator[T]:
        return iter(self.index.values())
