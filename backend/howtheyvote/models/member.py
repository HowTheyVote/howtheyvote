import datetime
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from structlog import get_logger

from ..files import member_photo_url, member_sharepic_url
from .common import BaseWithId
from .country import Country, CountryType
from .group import Group
from .national_party import NationalParty
from .types import DataclassType, ListType

log = get_logger(__name__)


@dataclass
class GroupMembership:
    term: int
    group: Group
    start_date: datetime.date
    end_date: datetime.date | None


@dataclass
class NationalPartyMembership:
    party: NationalParty
    start_date: datetime.date
    end_date: datetime.date | None


def serialize_group_membership(group_membership: GroupMembership) -> dict[str, Any]:
    return {
        "term": group_membership.term,
        "start_date": group_membership.start_date.isoformat(),
        "end_date": group_membership.end_date.isoformat()
        if group_membership.end_date
        else None,
        "group": group_membership.group.code,
    }


def deserialize_group_membership(
    group_membership: dict[str, Any],
) -> GroupMembership:
    end_date = group_membership.get("end_date")

    return GroupMembership(
        term=group_membership["term"],
        start_date=datetime.date.fromisoformat(group_membership["start_date"]),
        end_date=datetime.date.fromisoformat(end_date) if end_date else None,
        group=Group[group_membership["group"]],
    )


GroupMembershipType = DataclassType(
    serialize_group_membership,
    deserialize_group_membership,
)


def serialize_national_party_membership(
    party_membership: NationalPartyMembership,
) -> dict[str, Any]:
    return {
        "party": party_membership.party.id,
        "start_date": party_membership.start_date.isoformat(),
        "end_date": party_membership.end_date.isoformat()
        if party_membership.end_date
        else None,
    }


def deserialize_national_party_membership(
    national_party_membership: dict[str, Any],
) -> NationalPartyMembership:
    end_date = national_party_membership.get("end_date")

    return NationalPartyMembership(
        start_date=datetime.date.fromisoformat(national_party_membership["start_date"]),
        end_date=datetime.date.fromisoformat(end_date) if end_date else None,
        party=NationalParty[national_party_membership["party"]],
    )


NationalPartyMembershipType = DataclassType(
    serialize_national_party_membership,
    deserialize_national_party_membership,
)


class Member(BaseWithId):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(sa.Unicode)
    last_name: Mapped[str] = mapped_column(sa.Unicode)
    country: Mapped[Country] = mapped_column(CountryType)
    group_memberships: Mapped[list[GroupMembership]] = mapped_column(
        ListType(GroupMembershipType)
    )
    national_party_memberships: Mapped[list[NationalPartyMembership]] = mapped_column(
        ListType(NationalPartyMembershipType)
    )
    date_of_birth: Mapped[datetime.date | None] = mapped_column(sa.Date)
    terms: Mapped[list[int]] = mapped_column(sa.JSON, default=[])
    email: Mapped[str | None] = mapped_column(sa.Unicode)
    facebook: Mapped[str | None] = mapped_column(sa.Unicode)
    twitter: Mapped[str | None] = mapped_column(sa.Unicode)

    def group_at(self, date: datetime.date | datetime.datetime) -> Group | None:
        if isinstance(date, datetime.datetime):
            date = date.date()

        for group_membership in self.group_memberships:
            if group_membership.start_date <= date and (
                not group_membership.end_date or group_membership.end_date >= date
            ):
                return group_membership.group

        return None

    def national_party_at(
        self, date: datetime.date | datetime.datetime
    ) -> NationalParty | None:
        if isinstance(date, datetime.datetime):
            date = date.date()

        for national_party_membership in self.national_party_memberships:
            if national_party_membership.start_date <= date and (
                not national_party_membership.end_date
                or national_party_membership.end_date >= date
            ):
                return national_party_membership.party

        return None

    def photo_url(self, size: int | None = None) -> str:
        return member_photo_url(self.id, size)

    @property
    def sharepic_url(self) -> str:
        return member_sharepic_url(self.id)

    @property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name
