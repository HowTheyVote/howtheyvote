import datetime
import pathlib
from typing import TypedDict

from sqlalchemy import select
from structlog import get_logger

from ..db import Session
from ..models import Member, Vote
from .csvw_helpers import Table

log = get_logger(__name__)


class MemberRow(TypedDict):
    id: int
    """Member ID as used by the [MEP Directory](https://www.europarl.europa.eu/meps/en/home)."""

    first_name: str
    """First name"""

    last_name: str
    """Last name"""

    country_code: str
    """3-letter ISO-3166-1 code"""

    date_of_birth: datetime.date | None
    """Date of birth"""

    email: str | None
    """Email address"""

    facebook: str | None
    """Facebook profile URL"""

    twitter: str | None
    """Twitter account URL"""


class CountryRow(TypedDict):
    code: str
    """3-letter ISO-3166-1 code"""

    iso_alpha_2: str
    """2-letter ISO-3166-1 code"""

    label: str
    """Label as published by the Publications Office of the European Union"""


class GroupRow(TypedDict):
    code: str
    """Unique identifier for the political group"""

    official_label: str
    """Official label as published by the Publications Office of the European Union"""

    label: str
    """Label based on the official label. Prefixes and suffixes such as "Group" are
    removed for clarity."""

    short_label: str
    """Short label or abbreviation"""


class GroupMembershipRow(TypedDict):
    member_id: int
    """Member ID"""

    group_code: str
    """Group code"""

    term: int
    """Parliamentary term"""

    start_date: datetime.date
    """Start date"""

    end_date: datetime.date | None
    """End date. If empty, the MEP the membership is still active."""


class VoteRow(TypedDict):
    id: int
    """Vote ID"""

    timestamp: datetime.datetime
    """Date and time of the vote"""

    display_title: str | None
    """Title that can be used to refer to the vote. In most cases, this is the title
    published in the roll-call vote results. If the title in the roll-call vote results
    is empty, this falls back to the procedure title."""

    reference: str | None
    """Reference to a plenary document such as a report or a resolution"""

    description: str | None
    """Description of the vote as published in the roll-call vote results"""

    is_main: bool
    """Whether this vote is a main vote."""

    is_featured: bool
    """Whether this vote is featured. Currently, a vote is featured when we have found an
    official press release about the vote published by the European Parliament Newsroom.
    However, this is subject to change."""

    procedure_reference: str | None
    """Procedure reference as listed in the Legislative Observatory"""

    procedure_title: str | None
    """Title of the legislative procedure as listed in the Legislative Observatory"""


class MemberVoteRow(TypedDict):
    vote_id: int
    """Vote ID"""

    member_id: int
    """Member ID"""

    position: str
    """Vote position"""


class Export:
    def __init__(self, outdir: pathlib.Path):
        self.outdir = outdir
        self.outdir.mkdir(exist_ok=True)

    def run(self) -> None:
        self.export_members()
        self.export_votes()

    def export_members(self) -> None:
        log.info("Exporting members")

        members = Table(
            row_type=MemberRow,
            outdir=self.outdir,
            name="members",
            primary_key="id",
        )

        countries = Table(
            row_type=CountryRow,
            outdir=self.outdir,
            name="countries",
            primary_key="code",
        )

        groups = Table(
            row_type=GroupRow,
            outdir=self.outdir,
            name="groups",
            primary_key="code",
        )

        group_memberships = Table(
            row_type=GroupMembershipRow,
            outdir=self.outdir,
            name="group_memberships",
            primary_key=["member_id", "group_code", "start_date", "end_date"],
        )

        exported_group_codes = set()
        exported_country_codes = set()

        with members.open(), countries.open(), groups.open(), group_memberships.open():
            for member in Session.scalars(select(Member)):
                members.write_row(
                    {
                        "id": member.id,
                        "first_name": member.first_name,
                        "last_name": member.last_name,
                        "country_code": member.country.code,
                        "date_of_birth": member.date_of_birth,
                        "email": member.email,
                        "facebook": member.facebook,
                        "twitter": member.twitter,
                    }
                )

                if member.country.code not in exported_country_codes:
                    exported_country_codes.add(member.country.code)

                    if not member.country.iso_alpha_2:
                        raise Exception(
                            f"Country {member.country.label} does not have ISO-alpha-2 code"
                        )

                    countries.write_row(
                        {
                            "code": member.country.code,
                            "iso_alpha_2": member.country.iso_alpha_2,
                            "label": member.country.label,
                        }
                    )

                for gm in member.group_memberships:
                    if gm.group.code not in exported_group_codes:
                        exported_group_codes.add(gm.group.code)

                        groups.write_row(
                            {
                                "code": gm.group.code,
                                "official_label": gm.group.official_label,
                                "label": gm.group.label,
                                "short_label": gm.group.short_label,
                            }
                        )

                    group_memberships.write_row(
                        {
                            "member_id": member.id,
                            "group_code": gm.group.code,
                            "term": gm.term,
                            "start_date": gm.start_date,
                            "end_date": gm.end_date,
                        }
                    )

    def export_votes(self) -> None:
        log.info("Exporting votes")

        votes = Table(
            row_type=VoteRow,
            outdir=self.outdir,
            name="votes",
            primary_key="id",
        )

        member_votes = Table(
            row_type=MemberVoteRow,
            outdir=self.outdir,
            name="member_votes",
            primary_key=["member_id", "vote_id"],
        )

        with votes.open(), member_votes.open():
            query = select(Vote).execution_options(yield_per=500)
            result = Session.scalars(query)

            for idx, vote in enumerate(result):
                if idx % 1000 == 0:
                    log.info("Writing vote", index=idx)

                votes.write_row(
                    {
                        "id": vote.id,
                        "timestamp": vote.timestamp,
                        "display_title": vote.display_title,
                        "reference": vote.reference,
                        "description": vote.description,
                        "is_main": vote.is_main,
                        "is_featured": vote.is_featured,
                        "procedure_reference": vote.procedure_reference,
                        "procedure_title": vote.procedure_title,
                    }
                )

                for member_vote in vote.member_votes:
                    member_votes.write_row(
                        {
                            "vote_id": vote.id,
                            "member_id": member_vote.web_id,
                            "position": member_vote.position.value,
                        }
                    )
