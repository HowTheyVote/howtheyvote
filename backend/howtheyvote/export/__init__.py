import datetime
import pathlib
import shutil
import tempfile
from typing import Any, TypedDict

from sqlalchemy import func, select
from structlog import get_logger

from ..db import Session
from ..helpers import parse_procedure_reference
from ..models import (
    AmendmentAuthorCommittee,
    AmendmentAuthorGroup,
    Committee,
    Country,
    EurovocConcept,
    Member,
    OEILSubject,
    Vote,
)
from ..vote_stats import count_vote_positions
from .csvw_helpers import Table

log = get_logger(__name__)


DESCRIPTION = """
## Status
The dataset is experimental and the format of the tables may change in the future.

## License
The HowTheyVote.eu data is made available under an open license. If you use data published by HowTheyVote.eu please make sure you’ve read the [license terms](https://howtheyvote.eu/about#license) and provide proper attribution.
"""  # noqa: E501


class MemberRow(TypedDict):
    """Each row represents a Member of the European Parliament (MEP)."""

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
    """Each row represents an EU member state."""

    code: str
    """3-letter ISO-3166-1 code"""

    iso_alpha_2: str
    """2-letter ISO-3166-1 code"""

    label: str
    """Label as published by the Publications Office of the European Union"""


class GroupRow(TypedDict):
    """Each row represents a political group in the European Parliament."""

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
    """Each row represents a membership of an MEP in a political group.

    MEPs can change their political group during the term, i.e., each MEP is part of one or
    more political groups over the course of a term. Non-attached MEPs are a member of the
    `NI` group."""

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
    """Each row represents a roll-call vote in plenary."""

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
    """Whether this vote is a main vote. We classify certain votes as main votes based on
    the text description in the voting records published by Parliament. For example, if
    Parliament has voted on amendments, only the vote on the text as a whole is classified
    as a main vote. Certain votes such as votes on the agenda are not classified as main
    votes. This is not an official classification by the European Parliament and there may
    be false negatives."""

    procedure_reference: str | None
    """Procedure reference as listed in the Legislative Observatory"""

    procedure_title: str | None
    """Title of the legislative procedure as listed in the Legislative Observatory"""

    procedure_type: str | None
    """Procedure type as listed in the Legislative Observatory. This is a 3-letter code
    such as COD, RSP, or BUD."""

    procedure_stage: str | None
    """Stage of the procedure in which the vote took place. One of `OLP_FIRST_READING`,
    `OLP_SECOND_READING`, `OLP_THIRD_READING`.This field is only available for votes starting
    in 2024 and if the vote is part of an Ordinary Legislative Procedure."""

    count_for: int
    """Number of MEPs who voted in favor"""

    count_against: int
    """Number of MEPs who voted against"""

    count_abstention: int
    """Number of MEPs who abstained"""

    count_did_not_vote: int
    """Number of MEPs who didn’t participate in the vote"""

    result: str | None
    """Vote result. One of `ADOPTED`, `REJECTED`, `LAPSED`. This field is only available for
    votes starting in 2024."""


class MemberVoteRow(TypedDict):
    """Each row represents how an MEP voted in a roll-call vote."""

    vote_id: int
    """Vote ID"""

    member_id: int
    """Member ID"""

    position: str
    """Vote position. One of `FOR`, `AGAINST`, `ABSTENTION` if the MEP participated in the
    vote or `DID_NOT_VOTE` if the MEP wasn’t present for the vote. We currently do not
    differentiate between MEPs who did not vote with or without an excuse."""

    country_code: str
    """Country code"""

    group_code: str | None
    """Group code. This references the political group that the MEP was part of on the day
    of the vote. This is not necessarily the MEP’s current political group."""


class EurovocConceptRow(TypedDict):
    """Each row represents a concept from the [EuroVoc thesaurus](https://op.europa.eu/en/web/eu-vocabularies/dataset/-/resource?uri=http://publications.europa.eu/resource/dataset/eurovoc)
    that is referenced by at least one vote."""

    id: str
    """EuroVoc concept ID"""

    label: str
    """Label"""


class EurovocConceptVoteRow(TypedDict):
    """Each row represents an EuroVoc concept related to a vote. This information is sourced
    from [EUR-Lex](https://eur-lex.europa.eu/homepage.html) isn’t available for all votes. For
    example, EUR-Lex doesn’t contain information about motions for resolutions."""

    vote_id: int
    """Vote ID"""

    eurovoc_concept_id: str
    """EuroVoc concept ID"""


class OEILSubjectRow(TypedDict):
    """Each row represents a subject as used by the [Legislative Observatory](https://oeil.secure.europarl.europa.eu/oeil/en)
    that is referenced by at least one vote."""

    code: str
    """Code"""

    label: str
    """Label"""


class OEILSubjectVoteRow(TypedDict):
    """Each row represents a subject related to a vote."""

    vote_id: int
    """Vote ID"""

    oeil_subject_code: str
    """Subject code"""


class GeoAreaRow(TypedDict):
    """Each row represents a country, territory, or other geopolitical entity that is
    referenced by at least one vote. The information is based on the [reference dataset](https://op.europa.eu/en/web/eu-vocabularies/dataset/-/resource?uri=http://publications.europa.eu/resource/dataset/country)
    published by the EU Publications Office."""

    code: str
    """ISO 3166-1 alpha-3 code if available, otherwise a custom 3-letter code"""

    label: str
    """Label"""

    iso_alpha_2: str | None
    """ISO 3166-1 alpha-2 code if available"""


class GeoAreaVoteRow(TypedDict):
    """Country, territory, or other geopolitical entity related to a vote."""

    vote_id: int
    """Vote ID"""

    geo_area_code: str
    """Geographic area code"""


class CommitteeRow(TypedDict):
    """Each row represents a committee of the European Parliament."""

    code: str
    """Unique identifier of the committee"""

    label: str
    """Label"""

    abbreviation: str
    """Abbreviation"""


class ResponsibleCommitteeVoteRow(TypedDict):
    """Committee responsible for the legislative procedure a vote is part of."""

    vote_id: int
    """Vote ID"""

    committee_code: str
    """Committee code"""


class AmendmentAuthorVoteRow(TypedDict):
    """Authors of the vote if vote is amendment. Multiple authors result in multiple rows.
    This information is only available for votes starting in 2024."""

    vote_id: int
    """Vote ID"""

    author_type: str
    """Either GROUP, COMMITTEE, MEMBERS, ORALLY, ORIGINAL_TEXT, or RAPPORTEUR"""

    group_code: str
    """Group code, if applicable."""

    committee_code: str
    """Committee code, if applicable."""


class Export:
    def __init__(self, outdir: pathlib.Path):
        self.outdir = outdir

        self.members = Table(
            row_type=MemberRow,
            outdir=self.outdir,
            name="members",
            primary_key="id",
        )

        self.countries = Table(
            row_type=CountryRow,
            outdir=self.outdir,
            name="countries",
            primary_key="code",
        )

        self.groups = Table(
            row_type=GroupRow,
            outdir=self.outdir,
            name="groups",
            primary_key="code",
        )

        self.group_memberships = Table(
            row_type=GroupMembershipRow,
            outdir=self.outdir,
            name="group_memberships",
            primary_key=["member_id", "group_code", "start_date", "end_date"],
        )

        self.votes = Table(
            row_type=VoteRow,
            outdir=self.outdir,
            name="votes",
            primary_key="id",
        )

        self.member_votes = Table(
            row_type=MemberVoteRow,
            outdir=self.outdir,
            name="member_votes",
            primary_key=["member_id", "vote_id"],
        )

        self.eurovoc_concept_votes = Table(
            row_type=EurovocConceptVoteRow,
            outdir=self.outdir,
            name="eurovoc_concept_votes",
            primary_key=["vote_id", "eurovoc_concept_id"],
        )

        self.eurovoc_concepts = Table(
            row_type=EurovocConceptRow,
            outdir=self.outdir,
            name="eurovoc_concepts",
            primary_key=["id"],
        )

        self.oeil_subjects = Table(
            row_type=OEILSubjectRow,
            outdir=self.outdir,
            name="oeil_subjects",
            primary_key=["code"],
        )

        self.oeil_subject_votes = Table(
            row_type=OEILSubjectVoteRow,
            outdir=self.outdir,
            name="oeil_subject_votes",
            primary_key=["vote_id", "oeil_subject_code"],
        )

        self.geo_areas = Table(
            row_type=GeoAreaRow,
            outdir=self.outdir,
            name="geo_areas",
            primary_key=["code"],
        )

        self.geo_area_votes = Table(
            row_type=GeoAreaVoteRow,
            outdir=self.outdir,
            name="geo_area_votes",
            primary_key=["vote_id", "geo_area_code"],
        )

        self.committees = Table(
            row_type=CommitteeRow,
            outdir=self.outdir,
            name="committees",
            primary_key=["code"],
        )

        self.responsible_committee_votes = Table(
            row_type=ResponsibleCommitteeVoteRow,
            outdir=self.outdir,
            name="responsible_committee_votes",
            primary_key=["vote_id", "committee_code"],
        )

        self.amendment_authors = Table(
            row_type=AmendmentAuthorVoteRow,
            outdir=self.outdir,
            name="amendment_authors_votes",
            primary_key=["vote_id"],
        )

    def run(self) -> None:
        self.fetch_members()
        self.write_export_timestamp()
        self.write_readme(
            [
                self.members,
                self.countries,
                self.groups,
                self.group_memberships,
                self.votes,
                self.member_votes,
                self.eurovoc_concepts,
                self.eurovoc_concept_votes,
                self.oeil_subjects,
                self.oeil_subject_votes,
                self.geo_areas,
                self.geo_area_votes,
                self.committees,
                self.responsible_committee_votes,
                self.amendment_authors,
            ]
        )
        self.export_members()
        self.export_votes()
        self.export_eurovoc_concepts()
        self.export_oeil_subjects()
        self.export_geo_areas()
        self.export_committees()

    def fetch_members(self) -> None:
        self.members_by_id: dict[int, Member] = {}

        for member in Session.scalars(select(Member)):
            self.members_by_id[member.id] = member

    def write_readme(self, tables: list[Table[Any]]) -> None:
        readme = self.outdir.joinpath("README.md")
        blocks = [
            DESCRIPTION.strip(),
            "## Tables",
        ]

        for table in tables:
            blocks.append(f"### {table.get_filename()}")
            blocks.append(table.get_description())
            blocks.append(table.get_markdown())

        text = "\n\n".join(blocks) + "\n"
        readme.write_text(text)

    def write_export_timestamp(self) -> None:
        timestamp = self.outdir.joinpath("last_updated.txt")
        timestamp.write_text(datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"))

    def export_members(self) -> None:
        log.info("Exporting members")

        exported_group_codes = set()
        exported_country_codes = set()

        with (
            self.members.open() as members,
            self.countries.open() as countries,
            self.groups.open() as groups,
            self.group_memberships.open() as group_memberships,
        ):
            query = select(Member).order_by(Member.id)
            result = Session.scalars(query)

            for member in result:
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

                for gm in sorted(member.group_memberships, key=lambda gm: gm.start_date):
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

        with (
            self.votes.open() as votes,
            self.member_votes.open() as member_votes,
            self.eurovoc_concept_votes.open() as eurovoc_concept_votes,
            self.oeil_subject_votes.open() as oeil_subject_votes,
            self.geo_area_votes.open() as geo_area_votes,
            self.responsible_committee_votes.open() as responsible_committee_votes,
            self.amendment_authors.open() as amendment_author_votes,
        ):
            query = select(Vote).order_by(Vote.id).execution_options(yield_per=500)
            result = Session.scalars(query)

            for idx, vote in enumerate(result):
                if idx % 1000 == 0:
                    log.info("Writing vote", index=idx)

                position_counts = count_vote_positions(vote.member_votes)
                procedure_reference = (
                    parse_procedure_reference(vote.procedure_reference)
                    if vote.procedure_reference
                    else None
                )

                votes.write_row(
                    {
                        "id": vote.id,
                        "timestamp": vote.timestamp,
                        "display_title": vote.display_title,
                        "reference": vote.reference,
                        "description": vote.description,
                        "is_main": vote.is_main,
                        "procedure_reference": vote.procedure_reference,
                        "procedure_title": vote.procedure_title,
                        "procedure_type": (
                            procedure_reference["type"].value if procedure_reference else None
                        ),
                        "procedure_stage": (
                            vote.procedure_stage.value if vote.procedure_stage else None
                        ),
                        "count_for": position_counts["FOR"],
                        "count_against": position_counts["AGAINST"],
                        "count_abstention": position_counts["ABSTENTION"],
                        "count_did_not_vote": position_counts["DID_NOT_VOTE"],
                        "result": vote.result.value if vote.result else None,
                    }
                )

                for eurovoc_concept in vote.eurovoc_concepts:
                    eurovoc_concept_votes.write_row(
                        {
                            "vote_id": vote.id,
                            "eurovoc_concept_id": eurovoc_concept.id,
                        }
                    )

                for oeil_subject in vote.oeil_subjects:
                    oeil_subject_votes.write_row(
                        {
                            "vote_id": vote.id,
                            "oeil_subject_code": oeil_subject.code,
                        }
                    )

                for geo_area in vote.geo_areas:
                    geo_area_votes.write_row(
                        {
                            "vote_id": vote.id,
                            "geo_area_code": geo_area.code,
                        }
                    )

                for responsible_committee in vote.responsible_committees:
                    responsible_committee_votes.write_row(
                        {
                            "vote_id": vote.id,
                            "committee_code": responsible_committee.code,
                        }
                    )

                if vote.amendment_authors:
                    for author in vote.amendment_authors:
                        amendment_author_votes.write_row(
                            {
                                "vote_id": vote.id,
                                "author_type": author.type.value,
                                "group_code": author.group.code
                                if isinstance(author, AmendmentAuthorGroup) and author.group
                                else "",
                                "committee_code": author.committee.code
                                if isinstance(author, AmendmentAuthorCommittee)
                                and author.committee
                                else "",
                            }
                        )

                for member_vote in sorted(vote.member_votes, key=lambda mv: mv.web_id):
                    member = self.members_by_id[member_vote.web_id]
                    group = member.group_at(vote.timestamp)

                    member_votes.write_row(
                        {
                            "vote_id": vote.id,
                            "member_id": member_vote.web_id,
                            "position": member_vote.position.value,
                            # In theory, country and group are redundant here, but in practice,
                            # this is super handy to calculate stats by group/country.
                            "country_code": member.country.code,
                            "group_code": group.code if group else None,
                        }
                    )

    def export_eurovoc_concepts(self) -> None:
        log.info("Exporting EuroVoc concepts")

        with self.eurovoc_concepts.open() as eurovoc_concepts:
            exp = func.json_each(Vote.eurovoc_concepts).table_valued("value")
            query = (
                select(func.distinct(exp.c.value)).select_from(Vote, exp).order_by(exp.c.value)
            )
            concept_ids = Session.execute(query).scalars()

            for concept_id in concept_ids:
                # `if True else None` is a hack to make mypy treat this as a normal value
                # expression and not as a type expression. If this keeps causing type checking
                # issues we might want to reconsider the use of metaclasses for this purpose.
                # See: https://github.com/python/mypy/issues/15107
                concept = EurovocConcept[concept_id] if True else None
                eurovoc_concepts.write_row({"id": concept.id, "label": concept.label})

    def export_oeil_subjects(self) -> None:
        log.info("Exporting OEIL subjects")

        with self.oeil_subjects.open() as oeil_subjects:
            exp = func.json_each(Vote.oeil_subjects).table_valued("value")
            query = (
                select(func.distinct(exp.c.value)).select_from(Vote, exp).order_by(exp.c.value)
            )
            subject_codes = Session.execute(query).scalars()

            for subject_code in subject_codes:
                # `if True else None` is a hack to make mypy treat this as a normal value
                # expression and not as a type expression. If this keeps causing type checking
                # issues we might want to reconsider the use of metaclasses for this purpose.
                # See: https://github.com/python/mypy/issues/15107
                subject = OEILSubject[subject_code] if True else None
                oeil_subjects.write_row({"code": subject.code, "label": subject.label})

    def export_geo_areas(self) -> None:
        log.info("Exporting geographic areas")

        with self.geo_areas.open() as geo_areas:
            exp = func.json_each(Vote.geo_areas).table_valued("value")
            query = (
                select(func.distinct(exp.c.value)).select_from(Vote, exp).order_by(exp.c.value)
            )
            geo_area_codes = Session.execute(query).scalars()

            for geo_area_code in geo_area_codes:
                # `if True else None` is a hack to make mypy treat this as a normal value
                # expression and not as a type expression. If this keeps causing type checking
                # issues we might want to reconsider the use of metaclasses for this purpose.
                # See: https://github.com/python/mypy/issues/15107
                geo_area = Country[geo_area_code] if True else None
                geo_areas.write_row(
                    {
                        "code": geo_area.code,
                        "label": geo_area.label,
                        "iso_alpha_2": geo_area.iso_alpha_2,
                    }
                )

    def export_committees(self) -> None:
        log.info("Exporting committees")

        with self.committees.open() as committees:
            exp = func.json_each(Vote.responsible_committees).table_valued("value")
            query = (
                select(func.distinct(exp.c.value)).select_from(Vote, exp).order_by(exp.c.value)
            )
            committee_codes = Session.execute(query).scalars()

            for committee_code in committee_codes:
                committee = Committee[committee_code] if True else None
                committees.write_row(
                    {
                        "code": committee.code,
                        "label": committee.label,
                        "abbreviation": committee.abbreviation,
                    }
                )


def generate_export(path: pathlib.Path) -> None:
    with tempfile.TemporaryDirectory() as outdir:
        export = Export(outdir=pathlib.Path(outdir))
        export.run()
        log.info("Archiving CSV export")
        shutil.make_archive(str(path), "zip", outdir)
