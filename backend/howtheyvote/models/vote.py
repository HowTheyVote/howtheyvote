import dataclasses
import datetime
from enum import Enum
from typing import TypedDict

import sqlalchemy as sa
from flask import url_for
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator

from .committee import Committee, CommitteeType
from .common import BaseWithId, DataIssue
from .country import Country, CountryType
from .eurovoc import EurovocConcept, EurovocConceptType
from .oeil import OEILSubject, OEILSubjectType
from .types import ListType


class VoteResult(Enum):
    ADOPTED = "ADOPTED"
    REJECTED = "REJECTED"
    LAPSED = "LAPSED"
    WITHDRAWN = "WITHDRAWN"


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


@dataclasses.dataclass
class MemberVote:
    web_id: int
    position: VotePosition


class SerializedMemberVote(TypedDict):
    web_id: int
    position: str


def serialize_member_vote(member_vote: MemberVote | None) -> SerializedMemberVote | None:
    if not member_vote:
        return None

    return {
        "web_id": member_vote.web_id,
        "position": member_vote.position.value,
    }


def deserialize_member_vote(member_vote: SerializedMemberVote | None) -> MemberVote | None:
    if not member_vote:
        return None

    return MemberVote(
        web_id=member_vote["web_id"],
        position=VotePosition[member_vote["position"]],
    )


class MemberVoteType(TypeDecorator[MemberVote]):
    impl = sa.JSON
    cache_ok = True

    def process_bind_param(
        self, value: MemberVote | None, dialect: Dialect
    ) -> SerializedMemberVote | None:
        return serialize_member_vote(value)

    def process_result_value(
        self, value: SerializedMemberVote | None, dialect: Dialect
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
    rapporteur: Mapped[str | None] = mapped_column(sa.Unicode)
    reference: Mapped[str | None] = mapped_column(sa.Unicode)
    description: Mapped[str | None] = mapped_column(sa.Unicode)
    is_main: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    group_key: Mapped[str | None] = mapped_column(sa.Unicode)
    result: Mapped[VoteResult | None] = mapped_column(sa.Enum(VoteResult))
    member_votes: Mapped[list[MemberVote]] = mapped_column(ListType(MemberVoteType()))
    geo_areas: Mapped[list[Country]] = mapped_column(ListType(CountryType()))
    eurovoc_concepts: Mapped[list[EurovocConcept]] = mapped_column(
        ListType(EurovocConceptType())
    )
    oeil_subjects: Mapped[list[OEILSubject]] = mapped_column(ListType(OEILSubjectType()))
    responsible_committees: Mapped[list[Committee]] = mapped_column(ListType(CommitteeType()))
    press_release: Mapped[str | None] = mapped_column(sa.Unicode)
    issues: Mapped[list[DataIssue]] = mapped_column(ListType(sa.Enum(DataIssue)))

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


class VoteGroup(BaseWithId):
    __tablename__ = "vote_groups"

    id: Mapped[str] = mapped_column(sa.Unicode, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(sa.Date)
    issues: Mapped[list[DataIssue]] = mapped_column(ListType(sa.Enum(DataIssue)))
