import dataclasses
from typing import Any, Literal

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass
from .common import BaseWithId
from .types import ListType


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


@dataclasses.dataclass
class OEILSummarySection:
    type: Literal["Heading", "Paragraph"]
    content: str


def serialize_summary_section_vote(
    section: OEILSummarySection | None,
) -> dict[str, Any] | None:
    if section is None:
        return None

    return {
        "type": section.type,
        "content": section.content,
    }


def deserialize_summary_section_vote(
    section: dict[str, Any] | None,
) -> OEILSummarySection | None:
    if section is None:
        return None

    return OEILSummarySection(
        type=section["type"],
        content=section["content"],
    )


class SAOEILSummarySectionType(TypeDecorator[OEILSummarySection]):
    impl = sa.JSON

    def process_bind_param(
        self, value: OEILSummarySection | None, dialect: Dialect
    ) -> dict[str, Any] | None:
        return serialize_summary_section_vote(value)

    def process_result_value(
        self, value: dict[str, Any] | None, dialect: Dialect
    ) -> OEILSummarySection | None:
        return deserialize_summary_section_vote(value)


class OEILSummary(BaseWithId):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    content: Mapped[list[OEILSummarySection]] = mapped_column(
        ListType(SAOEILSummarySectionType())
    )
