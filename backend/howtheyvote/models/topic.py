import dataclasses

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass


class TopicMeta(type):
    def __getitem__(cls, key: str) -> "Topic":
        topic = topics.get(key)

        if not topic:
            raise KeyError()

        return topic


@dataclasses.dataclass(frozen=True)
class Topic(DeserializableDataclass, metaclass=TopicMeta):
    code: str
    label: str
    parent_code: str

    def __hash__(self) -> int:
        return hash(self.code)

    @classmethod
    def get(cls, key: str) -> "Topic | None":
        try:
            return cls[key]
        except KeyError:
            return None

    @property
    def parent(self) -> "Topic | None":
        if not self.parent_code:
            return None

        return Topic[self.parent_code]


topics = DataclassContainer(
    dataclass=Topic,
    file_path=DATA_DIR.joinpath("topics.json"),
    key_attr="code",
)
topics.load()


class TopicType(TypeDecorator[Topic]):
    impl = sa.Unicode
    cache_ok = True

    def process_bind_param(self, value: Topic | None, dialect: Dialect) -> str | None:
        if not value:
            return None

        return value.code

    def process_result_value(self, value: str | None, dialect: Dialect) -> Topic | None:
        if not value:
            return None

        return topics.get(value)
