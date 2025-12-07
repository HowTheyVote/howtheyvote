import dataclasses
import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, TypedDict

import sqlalchemy as sa
from flask import url_for
from sqlalchemy import ColumnElement, ForeignKey
from sqlalchemy.engine import Dialect
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from .committee import Committee, CommitteeType
from .common import BaseWithId
from .country import Country, CountryType
from .eurovoc import EurovocConcept, EurovocConceptType
from .group import Group
from .oeil_subject import OEILSubject, OEILSubjectType
from .types import ListType

if TYPE_CHECKING:
    from ..models import PressRelease


class VoteResult(Enum):
    ADOPTED = "ADOPTED"
    REJECTED = "REJECTED"
    LAPSED = "LAPSED"
    WITHDRAWN = "WITHDRAWN"


class VoteResultType(Enum):
    ROLL_CALL = "ROLL_CALL"
    ELECTRONICAL = "ELECTRONICAL"
    RAISE_HAND = "RAISE_HAND"
    SECRET = "SECRET"


class VotePosition(Enum):
    FOR = "FOR"
    AGAINST = "AGAINST"
    ABSTENTION = "ABSTENTION"
    DID_NOT_VOTE = "DID_NOT_VOTE"


class DocumentType(Enum):
    A = "A"  # Report
    B = "B"  # Resolution
    C = "C"  # Commission proposal
    RC = "RC"  # Joint resolution


class ProcedureType(Enum):
    # Based on the codes used by the Parliament in the Legislative Observatory
    COD = "COD"  # Ordinary legislative procedure
    CNS = "CNS"  # Consultation procedure
    APP = "APP"  # Consent procedure
    BUD = "BUD"  # Budgetary procedure
    DEC = "DEC"  # Discharge procedure
    BUI = "BUI"  # Budgetary initiative
    NLE = "NLE"  # Non-legislative enactments
    INL = "INL"  # Legislative initiative procedure
    INI = "INI"  # Own-initiative procedure
    RSP = "RSP"  # Resolutions on topical subjects
    REG = "REG"  # Parliament's Rules of Procedure
    IMM = "IMM"  # Member's immunity
    RSO = "RSO"  # Internal organisation decisions
    INS = "INS"  # Institutional procedure
    ACI = "ACI"  # Interinstitutional agreement procedure
    DEA = "DEA"  # Delegated acts procedure
    RPS = "RPS"  # Implementing acts

    # Historic procedures
    AVC = "AVC"  # Assent procedure
    SYN = "SYN"  # Cooperation procedure
    DCE = "DCE"  # Written declaration
    COS = "COS"  # Procedure on a strategy paper


class ProcedureStage(Enum):
    OLP_FIRST_READING = "OLP_FIRST_READING"
    OLP_SECOND_READING = "OLP_SECOND_READING"
    OLP_THIRD_READING = "OLP_THIRD_READING"


class AmendmentAuthorType(Enum):
    GROUP = "GROUP"
    COMMITTEE = "COMMITTEE"
    ORIGINAL_TEXT = "ORIGINAL_TEXT"
    MEMBERS = "MEMBERS"
    ORALLY = "ORALLY"
    RAPPORTEUR = "RAPPORTEUR"


@dataclasses.dataclass
class AmendmentAuthorGroup:
    group: Group | None

    @property
    def type(self) -> AmendmentAuthorType:
        return AmendmentAuthorType.GROUP


@dataclasses.dataclass
class AmendmentAuthorCommittee:
    committee: Committee | None

    @property
    def type(self) -> AmendmentAuthorType:
        return AmendmentAuthorType.COMMITTEE


@dataclasses.dataclass
class AmendmentAuthorOriginalText:
    @property
    def type(self) -> AmendmentAuthorType:
        return AmendmentAuthorType.ORIGINAL_TEXT


@dataclasses.dataclass
class AmendmentAuthorMembers:
    @property
    def type(self) -> AmendmentAuthorType:
        return AmendmentAuthorType.MEMBERS


@dataclasses.dataclass
class AmendmentAuthorOrally:
    @property
    def type(self) -> AmendmentAuthorType:
        return AmendmentAuthorType.ORALLY


@dataclasses.dataclass
class AmendmentAuthorRapporteur:
    @property
    def type(self) -> AmendmentAuthorType:
        return AmendmentAuthorType.RAPPORTEUR


AmendmentAuthor = (
    AmendmentAuthorGroup
    | AmendmentAuthorCommittee
    | AmendmentAuthorOriginalText
    | AmendmentAuthorMembers
    | AmendmentAuthorOrally
    | AmendmentAuthorRapporteur
)

AMENDMENT_AUTHOR_TYPE_TO_CLASS: dict[AmendmentAuthorType, type[AmendmentAuthor]] = {
    AmendmentAuthorType.GROUP: AmendmentAuthorGroup,
    AmendmentAuthorType.COMMITTEE: AmendmentAuthorCommittee,
    AmendmentAuthorType.ORIGINAL_TEXT: AmendmentAuthorOriginalText,
    AmendmentAuthorType.MEMBERS: AmendmentAuthorMembers,
    AmendmentAuthorType.ORALLY: AmendmentAuthorOrally,
    AmendmentAuthorType.RAPPORTEUR: AmendmentAuthorRapporteur,
}


def serialize_amendment_author(author: AmendmentAuthor | None) -> dict[str, Any] | None:
    if not author:
        return None

    if isinstance(author, AmendmentAuthorGroup):
        return {
            "type": AmendmentAuthorType.GROUP,
            "group": author.group.code if author.group else None,
        }

    if isinstance(author, AmendmentAuthorCommittee):
        return {
            "type": AmendmentAuthorType.COMMITTEE,
            "committee": author.committee.code if author.committee else None,
        }

    return {"type": author.type}


def deserialize_amendment_author(author: dict[str, Any] | None) -> AmendmentAuthor | None:
    if not author:
        return None

    type_ = AmendmentAuthorType[author["type"]]

    if type_ == AmendmentAuthorType.GROUP:
        return AmendmentAuthorGroup(group=Group[author["group"]] if author["group"] else None)

    if type_ == AmendmentAuthorType.COMMITTEE:
        return AmendmentAuthorCommittee(
            committee=Committee[author["committee"]] if author["committee"] else None,
        )

    author_class = AMENDMENT_AUTHOR_TYPE_TO_CLASS[type_]

    # Typing this correctly would require a lot of boilerplate. Skipping that
    # given that this is very isolated
    return author_class()  # type: ignore


class SAAmendmentAuthorType(TypeDecorator[AmendmentAuthor]):
    impl = sa.JSON
    cache_ok = True

    def process_bind_param(
        self, value: AmendmentAuthor | None, dialect: Dialect
    ) -> dict[str, Any] | None:
        if value is None:
            return None

        return serialize_amendment_author(value)

    def process_result_value(
        self, value: dict[str, Any] | None, dialect: Dialect
    ) -> AmendmentAuthor | None:
        if value is None:
            return None

        return deserialize_amendment_author(value)


@dataclasses.dataclass
class MemberVote:
    web_id: int
    position: VotePosition


def serialize_member_vote(member_vote: MemberVote | None) -> dict[str, Any] | None:
    if not member_vote:
        return None

    return {
        "web_id": member_vote.web_id,
        "position": member_vote.position.value,
    }


def deserialize_member_vote(member_vote: dict[str, Any] | None) -> MemberVote | None:
    if not member_vote:
        return None

    return MemberVote(
        web_id=member_vote["web_id"],
        position=VotePosition[member_vote["position"]],
    )


class SAMemberVoteType(TypeDecorator[MemberVote]):
    impl = sa.JSON
    cache_ok = True

    def process_bind_param(
        self, value: MemberVote | None, dialect: Dialect
    ) -> dict[str, Any] | None:
        return serialize_member_vote(value)

    def process_result_value(
        self, value: dict[str, Any] | None, dialect: Dialect
    ) -> MemberVote | None:
        return deserialize_member_vote(value)


class VotePositionCounts(TypedDict):
    FOR: int
    AGAINST: int
    ABSTENTION: int
    DID_NOT_VOTE: int


class Vote(BaseWithId):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(sa.DateTime)
    term: Mapped[int] = mapped_column(sa.Integer)
    order: Mapped[int] = mapped_column(sa.Integer)
    title: Mapped[str | None] = mapped_column(sa.Unicode)
    dlv_title: Mapped[str | None] = mapped_column(sa.Unicode)
    procedure_title: Mapped[str | None] = mapped_column(sa.Unicode)
    procedure_reference: Mapped[str | None] = mapped_column(sa.Unicode)
    procedure_stage: Mapped[ProcedureStage | None] = mapped_column(sa.Enum(ProcedureStage))
    amendment_subject: Mapped[str | None] = mapped_column(sa.Unicode)
    amendment_number: Mapped[str | None] = mapped_column(sa.Unicode)
    amendment_authors: Mapped[list[AmendmentAuthor] | None] = mapped_column(
        ListType(SAAmendmentAuthorType())
    )
    rapporteur: Mapped[str | None] = mapped_column(sa.Unicode)
    reference: Mapped[str | None] = mapped_column(sa.Unicode)
    texts_adopted_reference: Mapped[str | None] = mapped_column(sa.Unicode)
    description: Mapped[str | None] = mapped_column(sa.Unicode)
    is_main: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    group_key: Mapped[str | None] = mapped_column(sa.Unicode)
    result: Mapped[VoteResult | None] = mapped_column(sa.Enum(VoteResult))
    member_votes: Mapped[list[MemberVote]] = mapped_column(
        ListType(SAMemberVoteType()),
        default=[],
    )
    geo_areas: Mapped[list[Country]] = mapped_column(
        ListType(CountryType()),
        default=[],
    )
    eurovoc_concepts: Mapped[list[EurovocConcept]] = mapped_column(
        ListType(EurovocConceptType()),
        default=[],
    )
    oeil_subjects: Mapped[list[OEILSubject]] = mapped_column(
        ListType(OEILSubjectType()),
        default=[],
    )
    responsible_committees: Mapped[list[Committee]] = mapped_column(
        ListType(CommitteeType()),
        default=[],
    )
    press_release_id: Mapped[str | None] = mapped_column(ForeignKey("press_releases.id"))
    press_release: Mapped["PressRelease | None"] = relationship(back_populates="votes")
    oeil_summary_id: Mapped[int | None] = mapped_column(sa.Integer)

    @hybrid_property
    def date(self) -> datetime.date:
        return self.timestamp.date()

    @date.inplace.expression
    def _date_expression(cls) -> ColumnElement[datetime.date]:  # noqa: N805 (see https://github.com/astral-sh/ruff/issues/4604#issuecomment-1774659014)
        return sa.func.date(cls.timestamp)

    @property
    def display_title(self) -> str | None:
        if self.dlv_title:
            return self.dlv_title

        if (
            self.title
            and self.procedure_title
            and len(self.title) > 125
            and len(self.procedure_title) < len(self.title)
        ):
            return self.procedure_title

        return self.title or self.procedure_title

    @property
    def sharepic_url(self) -> str | None:
        if not self.is_main:
            return None

        return url_for("api.static_api.vote_sharepic", vote_id=self.id)
