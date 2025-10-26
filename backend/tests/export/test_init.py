import datetime
import re

import time_machine

from howtheyvote.export import Export
from howtheyvote.models import (
    Committee,
    Country,
    EurovocConcept,
    Group,
    GroupMembership,
    Member,
    MemberVote,
    OEILSubject,
    ProcedureStage,
    Vote,
    VotePosition,
    VoteResult,
)


def test_readme(db_session, tmp_path):
    export = Export(outdir=tmp_path)
    export.run()

    readme = tmp_path.joinpath("README.md").read_text()

    assert re.search(r"^## Status$", readme, re.MULTILINE)
    assert re.search(r"^## License$", readme, re.MULTILINE)
    assert re.search(r"^## Tables$", readme, re.MULTILINE)
    assert re.search(r"^### members.csv$", readme, re.MULTILINE)
    assert re.search(r"^### votes.csv$", readme, re.MULTILINE)


def test_last_updated(db_session, tmp_path):
    export = Export(outdir=tmp_path)

    with time_machine.travel(datetime.datetime(2025, 1, 1, 0, 0, 0, 123456)):
        export.run()

    last_updated = tmp_path.joinpath("last_updated.txt").read_text()
    assert last_updated == "2025-01-01T00:00:00+00:00"


def test_export_members(db_session, tmp_path):
    member = Member(
        id=123,
        first_name="Max",
        last_name="MUSTERMANN",
        country=Country["DEU"],
        date_of_birth=datetime.date(1960, 1, 1),
        group_memberships=[
            GroupMembership(
                group=Group["EPP"],
                term=9,
                start_date=datetime.date(2024, 1, 1),
                end_date=None,
            ),
        ],
    )
    db_session.add(member)
    db_session.commit()

    export = Export(outdir=tmp_path)
    export.run()

    members_csv = tmp_path.joinpath("members.csv")
    members_meta = tmp_path.joinpath("members.csv-metadata.json")

    expected = (
        "id,first_name,last_name,country_code,date_of_birth,email,facebook,twitter\n"
        "123,Max,MUSTERMANN,DEU,1960-01-01,,,\n"
    )

    assert members_csv.read_text() == expected
    assert members_meta.is_file()

    countries_csv = tmp_path.joinpath("countries.csv")
    countries_meta = tmp_path.joinpath("countries.csv-metadata.json")

    expected = "code,iso_alpha_2,label\nDEU,DE,Germany\n"

    assert countries_csv.read_text() == expected
    assert countries_meta.is_file()

    groups_csv = tmp_path.joinpath("groups.csv")
    groups_meta = tmp_path.joinpath("groups.csv-metadata.json")

    expected = (
        "code,official_label,label,short_label\n"
        "EPP,Group of the European People’s Party,European People’s Party,EPP\n"
    )

    assert groups_csv.read_text() == expected
    assert groups_meta.is_file()

    group_memberships_csv = tmp_path.joinpath("group_memberships.csv")
    group_memberships_meta = tmp_path.joinpath("group_memberships.csv-metadata.json")

    expected = "member_id,group_code,term,start_date,end_date\n123,EPP,9,2024-01-01,\n"

    assert group_memberships_csv.read_text() == expected
    assert group_memberships_meta.is_file()


def test_export_votes(db_session, tmp_path):
    member = Member(
        id=123,
        first_name="Max",
        last_name="MUSTERMANN",
        country=Country["DEU"],
        date_of_birth=datetime.date(1960, 1, 1),
        group_memberships=[
            GroupMembership(
                group=Group["EPP"],
                term=9,
                start_date=datetime.date(2024, 1, 1),
                end_date=None,
            ),
        ],
    )

    vote = Vote(
        id=123456,
        title="Lorem Ipsum",
        timestamp=datetime.datetime(2024, 1, 1, 0, 0, 0),
        procedure_title="Lorem Ipsum",
        procedure_reference="2025/1234(COD)",
        procedure_stage=ProcedureStage.OLP_FIRST_READING,
        member_votes=[
            MemberVote(
                web_id=123,
                position=VotePosition.FOR,
            ),
        ],
        eurovoc_concepts=[
            EurovocConcept["4057"],
            EurovocConcept["1460"],
        ],
        oeil_subjects=[
            OEILSubject["2.50.04"],
        ],
        geo_areas=[
            Country["MDA"],
            Country["RUS"],
        ],
        responsible_committees=[Committee["AFET"]],
        result=VoteResult.ADOPTED,
        amendment_subject=None,
        amendment_number=None,
        texts_adopted_reference="A10-123-123",
    )

    db_session.add_all([member, vote])
    db_session.commit()

    export = Export(outdir=tmp_path)
    export.run()

    votes_csv = tmp_path.joinpath("votes.csv")
    votes_meta = tmp_path.joinpath("votes.csv-metadata.json")

    expected = (
        "id,timestamp,display_title,reference,description,amendment_subject,amendment_number,is_main,procedure_reference,procedure_title,procedure_type,procedure_stage,count_for,count_against,count_abstention,count_did_not_vote,result,adopted_text_reference\n"
        "123456,2024-01-01 00:00:00,Lorem Ipsum,,,,,False,2025/1234(COD),Lorem Ipsum,COD,OLP_FIRST_READING,1,0,0,0,ADOPTED,A10-123-123\n"
    )

    assert votes_csv.read_text() == expected
    assert votes_meta.is_file()

    member_votes_csv = tmp_path.joinpath("member_votes.csv")
    member_votes_meta = tmp_path.joinpath("member_votes.csv-metadata.json")

    expected = "vote_id,member_id,position,country_code,group_code\n123456,123,FOR,DEU,EPP\n"

    assert member_votes_csv.read_text() == expected
    assert member_votes_meta.is_file()

    eurovoc_concept_votes_csv = tmp_path.joinpath("eurovoc_concept_votes.csv")
    eurovoc_concept_votes_meta = tmp_path.joinpath("eurovoc_concept_votes.csv-metadata.json")

    expected = "vote_id,eurovoc_concept_id\n123456,4057\n123456,1460\n"

    assert eurovoc_concept_votes_csv.read_text() == expected
    assert eurovoc_concept_votes_meta.is_file()

    eurovoc_concepts_csv = tmp_path.joinpath("eurovoc_concepts.csv")
    eurovoc_concepts_meta = tmp_path.joinpath("eurovoc_concepts.csv-metadata.json")

    expected = "id,label\n1460,EU financial instrument\n4057,enlargement of the Union\n"

    assert eurovoc_concepts_csv.read_text() == expected
    assert eurovoc_concepts_meta.is_file()

    oeil_subject_votes_csv = tmp_path.joinpath("oeil_subject_votes.csv")
    oeil_subject_votes_meta = tmp_path.joinpath("oeil_subject_votes.csv-metadata.json")

    expected = "vote_id,oeil_subject_code\n123456,2.50.04\n"

    assert oeil_subject_votes_csv.read_text() == expected
    assert oeil_subject_votes_meta.is_file()

    oeil_subjects_csv = tmp_path.joinpath("oeil_subjects.csv")
    oeil_subjects_meta = tmp_path.joinpath("oeil_subjects.csv-metadata.json")

    expected = "code,label\n2.50.04,Banks and credit\n"

    assert oeil_subjects_csv.read_text() == expected
    assert oeil_subjects_meta.is_file()

    geo_area_votes_csv = tmp_path.joinpath("geo_area_votes.csv")
    geo_area_votes_meta = tmp_path.joinpath("geo_area_votes.csv-metadata.json")

    expected = "vote_id,geo_area_code\n123456,MDA\n123456,RUS\n"

    assert geo_area_votes_csv.read_text() == expected
    assert geo_area_votes_meta.is_file()

    geo_areas_csv = tmp_path.joinpath("geo_areas.csv")
    geo_areas_meta = tmp_path.joinpath("geo_areas.csv-metadata.json")

    expected = "code,label,iso_alpha_2\nMDA,Moldova,MD\nRUS,Russia,RU\n"

    assert geo_areas_csv.read_text() == expected
    assert geo_areas_meta.is_file()

    responsible_committee_votes_csv = tmp_path.joinpath("responsible_committee_votes.csv")
    responsible_committee_votes_meta = tmp_path.joinpath(
        "responsible_committee_votes.csv-metadata.json"
    )

    expected = "vote_id,committee_code\n123456,AFET\n"

    assert responsible_committee_votes_csv.read_text() == expected
    assert responsible_committee_votes_meta.is_file()

    committees_csv = tmp_path.joinpath("committees.csv")
    committees_meta = tmp_path.joinpath("committees.csv-metadata.json")

    expected = "code,label,abbreviation\nAFET,Foreign Affairs,AFET\n"

    assert committees_csv.read_text() == expected
    assert committees_meta.is_file()


def test_export_votes_country_group(db_session, tmp_path):
    member = Member(
        id=123,
        first_name="Max",
        last_name="MUSTERMANN",
        country=Country["DEU"],
        date_of_birth=datetime.date(1960, 1, 1),
        group_memberships=[
            GroupMembership(
                group=Group["EPP"],
                term=9,
                start_date=datetime.date(2023, 1, 1),
                end_date=datetime.date(2024, 1, 31),
            ),
            GroupMembership(
                group=Group["RENEW"],
                term=9,
                start_date=datetime.date(2024, 2, 1),
                end_date=None,
            ),
        ],
    )

    one = Vote(
        id=123456,
        title="One",
        timestamp=datetime.datetime(2024, 1, 31, 0, 0, 0),
        member_votes=[
            MemberVote(
                web_id=123,
                position=VotePosition.FOR,
            ),
        ],
    )

    two = Vote(
        id=654321,
        title="Two",
        timestamp=datetime.datetime(2024, 2, 1, 0, 0, 0),
        member_votes=[
            MemberVote(
                web_id=123,
                position=VotePosition.FOR,
            ),
        ],
    )

    db_session.add_all([member, one, two])
    db_session.commit()

    export = Export(outdir=tmp_path)
    export.run()

    member_votes_csv = tmp_path.joinpath("member_votes.csv")

    expected = (
        "vote_id,member_id,position,country_code,group_code\n"
        "123456,123,FOR,DEU,EPP\n"
        "654321,123,FOR,DEU,RENEW\n"
    )

    assert member_votes_csv.read_text() == expected
