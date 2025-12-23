import dataclasses

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass


class OEILSubjectMeta(type):
    def __getitem__(cls, key: str) -> "OEILSubject":
        subject = oeil_subjects.get(key)

        if not subject:
            raise KeyError()

        return subject


@dataclasses.dataclass(frozen=True)
class OEILSubject(DeserializableDataclass, metaclass=OEILSubjectMeta):
    code: str
    label: str
    parent_code: str

    def __hash__(self) -> int:
        return hash(self.code)

    @classmethod
    def get(cls, key: str) -> "OEILSubject | None":
        try:
            return cls[key]
        except KeyError:
            return None

    @property
    def parent(self) -> "OEILSubject | None":
        if not self.parent_code:
            return None

        return OEILSubject[self.parent_code]

    @property
    def parents(self) -> set["OEILSubject"]:
        parents = set()

        if self.parent:
            parents.add(self.parent)
            parents.update(self.parent.parents)

        return parents


oeil_subjects = DataclassContainer(
    dataclass=OEILSubject,
    file_path=DATA_DIR.joinpath("oeil_subjects.json"),
    key_attr="code",
)
oeil_subjects.load()


class OEILSubjectType(TypeDecorator[OEILSubject]):
    impl = sa.Unicode
    cache_ok = True

    def process_bind_param(self, value: OEILSubject | None, dialect: Dialect) -> str | None:
        if not value:
            return None

        return value.code

    def process_result_value(self, value: str | None, dialect: Dialect) -> OEILSubject | None:
        if not value:
            return None

        return oeil_subjects.get(value)
