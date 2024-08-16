import datetime
import re

from howtheyvote.export import Export
from howtheyvote.models import (
    Country,
    Group,
    GroupMembership,
    Member,
    MemberVote,
    Vote,
    VotePosition,
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

    expected = "code,iso_alpha_2,label\n" "DEU,DE,Germany\n"

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

    expected = "member_id,group_code,term,start_date,end_date\n" "123,EPP,9,2024-01-01,\n"

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
        member_votes=[
            MemberVote(
                web_id=123,
                position=VotePosition.FOR,
            ),
        ],
    )

    db_session.add_all([member, vote])
    db_session.commit()

    export = Export(outdir=tmp_path)
    export.run()

    votes_csv = tmp_path.joinpath("votes.csv")
    votes_meta = tmp_path.joinpath("votes.csv-metadata.json")

    expected = (
        "id,timestamp,display_title,reference,description,is_main,is_featured,procedure_reference,procedure_title\n"
        "123456,2024-01-01 00:00:00,Lorem Ipsum,,,False,False,,\n"
    )

    assert votes_csv.read_text() == expected
    assert votes_meta.is_file()

    member_votes_csv = tmp_path.joinpath("member_votes.csv")
    member_votes_meta = tmp_path.joinpath("member_votes.csv-metadata.json")

    expected = (
        "vote_id,member_id,position,country_code,group_code\n" "123456,123,FOR,DEU,EPP\n"
    )

    assert member_votes_csv.read_text() == expected
    assert member_votes_meta.is_file()


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
