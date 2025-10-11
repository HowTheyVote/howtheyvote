import dataclasses
import datetime

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass


class CommitteeMeta(type):
    def __getitem__(cls, key: str) -> "Committee":
        committee = committees.get(key)

        if not committee:
            raise KeyError()

        return committee


@dataclasses.dataclass(frozen=True)
class Committee(DeserializableDataclass, metaclass=CommitteeMeta):
    code: str
    official_label: str
    label: str
    abbreviation: str
    start_date: datetime.date
    end_date: datetime.date | None

    def __hash__(self) -> int:
        return hash(self.code)

    @classmethod
    def get(cls, key: str) -> "Committee | None":
        try:
            return cls[key]
        except KeyError:
            return None


committees = DataclassContainer(
    dataclass=Committee,
    file_path=DATA_DIR.joinpath("committees.json"),
    key_attr="code",
)
committees.load()


class CommitteeType(TypeDecorator[Committee]):
    impl = sa.Unicode
    cache_ok = True

    def process_bind_param(self, value: Committee | None, dialect: Dialect) -> str | None:
        if not value:
            return None

        return value.code

    def process_result_value(self, value: str | None, dialect: Dialect) -> Committee | None:
        if not value:
            return None

        return committees.get(value)
