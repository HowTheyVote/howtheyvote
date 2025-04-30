import datetime

import pytest

from howtheyvote.models import (
    Country,
    Fragment,
    Group,
    GroupMembership,
    Member,
    MemberVote,
    Vote,
    VotePosition,
    VoteResult,
)
from howtheyvote.store import index_search


@pytest.fixture()
def records(db_session):
    john = Member(
        id=1,
        first_name="John",
        last_name="Doe",
        country=Country["FRA"],
        terms=[9],
        group_memberships=[
            GroupMembership(
                term=9,
                start_date=datetime.date(2022, 1, 1),
                end_date=datetime.date(2022, 12, 31),
                group=Group["NI"],
            ),
            GroupMembership(
                term=9,
                start_date=datetime.date(2023, 1, 1),
                end_date=None,
                group=Group["GUE_NGL"],
            ),
        ],
    )

    jane = Member(
        id=2,
        first_name="Jane",
        last_name="Smith",
        country=Country["DEU"],
        terms=[9],
        group_memberships=[
            GroupMembership(
                term=9,
                start_date=datetime.date(2023, 1, 1),
                end_date=datetime.date(2023, 12, 31),
                group=Group["EPP"],
            ),
        ],
    )

    vote = Vote(
        id=1,
        timestamp=datetime.datetime(2023, 1, 1, 0, 0, 0),
        order=1,
        title="Should we have pizza for lunch?",
        description="Am 123",
        procedure_reference="1234/2025(COD)",
        member_votes=[
            MemberVote(
                web_id=1,
                position=VotePosition.FOR,
            ),
            MemberVote(
                web_id=2,
                position=VotePosition.AGAINST,
            ),
        ],
        result=VoteResult.ADOPTED,
    )

    db_session.add_all([john, jane, vote])
    db_session.commit()


def test_votes_api_index(db_session, api):
    one = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1, 9, 0, 0),
        title="Vote One",
        is_main=True,
        result=VoteResult.ADOPTED,
    )

    two = Vote(
        id=2,
        timestamp=datetime.datetime(2024, 1, 1, 10, 0, 0),
        title="Vote Two",
        is_main=True,
        result=VoteResult.REJECTED,
    )

    amendment = Vote(
        id=3,
        timestamp=datetime.datetime(2024, 1, 1, 10, 0, 0),
        title="Vote Two",
        description="Am 123",
        is_main=False,
    )

    db_session.add_all([one, two, amendment])
    db_session.commit()

    res = api.get("/api/votes")
    assert res.json["total"]
    assert res.json["page"] == 1
    assert res.json["page_size"] == 20
    assert res.json["has_prev"] is False
    assert res.json["has_next"] is False

    assert len(res.json["results"]) == 2
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][0]["display_title"] == "Vote Two"
    assert res.json["results"][0]["result"] == "REJECTED"
    assert res.json["results"][1]["id"] == 1
    assert res.json["results"][1]["display_title"] == "Vote One"
    assert res.json["results"][1]["result"] == "ADOPTED"

    res = api.get("/api/votes", query_string={"page": 1, "page_size": 1})
    assert res.json["total"] == 2
    assert res.json["page"] == 1
    assert res.json["page_size"] == 1
    assert res.json["has_prev"] is False
    assert res.json["has_next"] is True

    assert len(res.json["results"]) == 1
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][0]["display_title"] == "Vote Two"

    res = api.get("/api/votes", query_string={"page": 2, "page_size": 1})
    assert res.json["total"] == 2
    assert res.json["page"] == 2
    assert res.json["page_size"] == 1
    assert res.json["has_prev"] is True
    assert res.json["has_next"] is False

    assert len(res.json["results"]) == 1
    assert res.json["results"][0]["id"] == 1
    assert res.json["results"][0]["display_title"] == "Vote One"


def test_votes_api_index_empty_title(db_session, api):
    empty_title = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1, 0, 0, 0),
        is_main=True,
    )

    non_empty_vote_title = Vote(
        id=2,
        timestamp=datetime.datetime(2024, 1, 2, 0, 0, 0),
        title="Vote title",
        is_main=True,
    )

    non_empty_procedure_title = Vote(
        id=3,
        timestamp=datetime.datetime(2024, 1, 3, 0, 0, 0),
        title="Procedure title",
        is_main=True,
    )

    db_session.add_all([empty_title, non_empty_vote_title, non_empty_procedure_title])
    db_session.commit()

    res = api.get("/api/votes")
    assert len(res.json["results"]) == 2
    assert res.json["results"][0]["display_title"] == "Procedure title"
    assert res.json["results"][1]["display_title"] == "Vote title"


def test_votes_api_index_sort(db_session, api):
    one = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1, 0, 0, 0),
        title="Vote One",
        reference="A9-0043/2024",
        procedure_reference="2022/0362(NLE)",
        is_main=True,
    )

    two = Vote(
        id=2,
        timestamp=datetime.datetime(2024, 7, 1, 0, 0, 0),
        title="Vote Two",
        reference="A9-0282/2023",
        procedure_reference="2022/2148(INI)",
        is_main=True,
    )

    db_session.add_all([one, two])
    db_session.commit()

    # By default, results are sorted by timestamp in descending order
    res = api.get("/api/votes")
    assert res.json["total"] == 2
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][1]["id"] == 1

    # Sorting can be controlled via query params
    res = api.get(
        "/api/votes",
        query_string={
            "sort_by": "timestamp",
            "sort_order": "asc",
        },
    )
    assert res.json["total"] == 2
    assert res.json["results"][0]["id"] == 1
    assert res.json["results"][1]["id"] == 2

    res = api.get(
        "/api/votes",
        query_string={
            "sort_by": "timestamp",
            "sort_order": "desc",
        },
    )
    assert res.json["total"] == 2
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][1]["id"] == 1

    # Ignores invalid parameters
    res = api.get(
        "/api/votes",
        query_string={
            "sort_by": "invalid",
            "sort_order": "invalid",
        },
    )
    assert res.status_code == 200
    assert res.json["total"] == 2


def test_votes_api_search(db_session, search_index, api):
    one = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1, 9, 0, 0),
        title="Vote One",
        is_main=True,
    )

    two = Vote(
        id=2,
        timestamp=datetime.datetime(2024, 1, 1, 10, 0, 0),
        title="Vote Two",
        is_main=True,
    )

    db_session.add_all([one, two])
    db_session.commit()
    index_search(Vote, [one, two])

    res = api.get("/api/votes/search")
    assert res.json["total"] == 2
    assert len(res.json["results"]) == 2
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][0]["display_title"] == "Vote Two"
    assert res.json["results"][1]["id"] == 1
    assert res.json["results"][1]["display_title"] == "Vote One"

    res = api.get("/api/votes/search", query_string={"q": "vote"})
    assert res.json["total"] == 2
    assert len(res.json["results"]) == 2
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][0]["display_title"] == "Vote Two"
    assert res.json["results"][1]["id"] == 1
    assert res.json["results"][1]["display_title"] == "Vote One"

    res = api.get("/api/votes/search", query_string={"q": "two"})
    assert res.json["total"] == 1
    assert len(res.json["results"]) == 1
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][0]["display_title"] == "Vote Two"

    # Ignores invalid parameters
    res = api.get(
        "/api/votes/search",
        query_string={
            "q": "vote",
            "sort_by": "invalid",
            "sort_order": "invalid",
        },
    )
    assert res.status_code == 200
    assert res.json["total"] == 2


def test_votes_api_search_references(db_session, search_index, api):
    one = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1, 9, 0, 0),
        title="Vote One",
        reference="A9-0043/2024",
        procedure_reference="2022/0362(NLE)",
        is_main=True,
    )

    two = Vote(
        id=2,
        timestamp=datetime.datetime(2024, 1, 1, 10, 0, 0),
        title="Vote Two",
        reference="A9-0282/2023",
        procedure_reference="2022/2148(INI)",
        is_main=True,
    )

    db_session.add_all([one, two])
    db_session.commit()
    index_search(Vote, [one, two])

    res = api.get("/api/votes/search", query_string={"q": "A9-0043/2024"})
    assert res.json["total"] == 1
    assert res.json["results"][0]["id"] == 1

    res = api.get("/api/votes/search", query_string={"q": "2022/2148(INI)"})
    assert res.json["total"] == 1
    assert res.json["results"][0]["id"] == 2

    res = api.get("/api/votes/search", query_string={"q": "A9-0043/2024 2022/0362(NLE)"})
    assert res.json["total"] == 1
    assert res.json["results"][0]["id"] == 1

    res = api.get("/api/votes/search", query_string={"q": "A9-0043/2024 2022/2148(INI)"})
    assert res.json["total"] == 0

    # At the moment, this will only match votes with the correct reference and that contain
    # the remaining query terms. Maybe reconsider this in the future, could be more intuitive
    # to make it an OR, simply ranking votes that match both higher.
    res = api.get("/api/votes/search", query_string={"q": "two A9-0043/2024"})
    assert res.json["total"] == 0


def test_votes_api_search_sort(db_session, search_index, api):
    one = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1, 0, 0, 0),
        title="Vote One",
        reference="A9-0043/2024",
        procedure_reference="2022/0362(NLE)",
        is_main=True,
    )

    two = Vote(
        id=2,
        timestamp=datetime.datetime(2024, 7, 1, 0, 0, 0),
        title="Vote Two",
        reference="A9-0282/2023",
        procedure_reference="2022/2148(INI)",
        is_main=True,
    )

    db_session.add_all([one, two])
    db_session.commit()
    index_search(Vote, [one, two])

    # If all results are equally relevant, results are sorted by timestamp in descending order
    res = api.get("/api/votes/search", query_string={"q": "vote"})
    assert res.json["total"] == 2
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][1]["id"] == 1

    # By default, results are sorted by relevance
    res = api.get("/api/votes/search", query_string={"q": "vote one"})
    assert res.json["total"] == 2
    assert res.json["results"][0]["id"] == 1
    assert res.json["results"][1]["id"] == 2

    # Sorting can be controlled via query params
    res = api.get(
        "/api/votes/search",
        query_string={
            "q": "vote",
            "sort_by": "timestamp",
            "sort_order": "asc",
        },
    )
    assert res.json["total"] == 2
    assert res.json["results"][0]["id"] == 1
    assert res.json["results"][1]["id"] == 2

    res = api.get(
        "/api/votes/search",
        query_string={
            "q": "vote",
            "sort_by": "timestamp",
            "sort_order": "desc",
        },
    )
    assert res.json["total"] == 2
    assert res.json["results"][0]["id"] == 2
    assert res.json["results"][1]["id"] == 1


def test_votes_api_search_special_chars(db_session, search_index, api):
    vote = Vote(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1, 0, 0, 0),
        title="Union Secure Connectivity Programme 2023-2027",
        is_main=True,
    )
    db_session.add(vote)
    db_session.commit()
    index_search(Vote, [vote])

    res = api.get(
        "/api/votes/search",
        query_string={
            "q": "Union Secure Connectivity Programme 2023-2027",
        },
    )

    assert res.status_code == 200
    assert len(res.json["results"]) == 1
    assert res.json["results"][0]["id"] == 1


def test_votes_api_show(records, db_session, api):
    fragment = Fragment(
        model="Vote",
        group_key="1",
        source_name="RCVListScraper",
        source_id="1",
        source_url="https://europarl.europa.eu/vote-results.xml",
        timestamp=datetime.datetime(2023, 1, 1, 12, 0, 0),
        data={},
    )

    db_session.add(fragment)
    db_session.commit()

    res = api.get("/api/votes/1")

    expected = {
        "id": 1,
        "display_title": "Should we have pizza for lunch?",
        "timestamp": "2023-01-01T00:00:00",
        "reference": None,
        "description": "Am 123",
        "procedure": {
            "title": None,
            "type": "COD",
            "reference": "1234/2025(COD)",
            "stage": None,
        },
        "facts": None,
        "sharepic_url": None,
        "stats": {
            "total": {
                "FOR": 1,
                "AGAINST": 1,
                "ABSTENTION": 0,
                "DID_NOT_VOTE": 0,
            },
            "by_group": [
                {
                    "group": {
                        "code": "GUE_NGL",
                        "label": "The Left in the European Parliament – GUE/NGL",
                        "short_label": "GUE/NGL",
                    },
                    "stats": {
                        "FOR": 1,
                        "AGAINST": 0,
                        "ABSTENTION": 0,
                        "DID_NOT_VOTE": 0,
                    },
                },
                {
                    "group": {
                        "code": "EPP",
                        "label": "European People’s Party",
                        "short_label": "EPP",
                    },
                    "stats": {
                        "FOR": 0,
                        "AGAINST": 1,
                        "ABSTENTION": 0,
                        "DID_NOT_VOTE": 0,
                    },
                },
            ],
            "by_country": [
                {
                    "country": {
                        "code": "FRA",
                        "iso_alpha_2": "FR",
                        "label": "France",
                    },
                    "stats": {
                        "FOR": 1,
                        "AGAINST": 0,
                        "ABSTENTION": 0,
                        "DID_NOT_VOTE": 0,
                    },
                },
                {
                    "country": {
                        "code": "DEU",
                        "iso_alpha_2": "DE",
                        "label": "Germany",
                    },
                    "stats": {
                        "FOR": 0,
                        "AGAINST": 1,
                        "ABSTENTION": 0,
                        "DID_NOT_VOTE": 0,
                    },
                },
            ],
        },
        "member_votes": [
            {
                "position": "FOR",
                "member": {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "terms": [9],
                    "country": {
                        "code": "FRA",
                        "iso_alpha_2": "FR",
                        "label": "France",
                    },
                    "group": {
                        "code": "GUE_NGL",
                        "label": "The Left in the European Parliament – GUE/NGL",
                        "short_label": "GUE/NGL",
                    },
                    "photo_url": "/api/static/members/1.jpg",
                    "thumb_url": "/api/static/members/1-104.jpg",
                    "date_of_birth": None,
                    "email": None,
                    "facebook": None,
                    "twitter": None,
                },
            },
            {
                "position": "AGAINST",
                "member": {
                    "id": 2,
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "terms": [9],
                    "country": {
                        "code": "DEU",
                        "iso_alpha_2": "DE",
                        "label": "Germany",
                    },
                    "group": {
                        "code": "EPP",
                        "label": "European People’s Party",
                        "short_label": "EPP",
                    },
                    "photo_url": "/api/static/members/2.jpg",
                    "thumb_url": "/api/static/members/2-104.jpg",
                    "date_of_birth": None,
                    "email": None,
                    "facebook": None,
                    "twitter": None,
                },
            },
        ],
        "result": "ADOPTED",
        "geo_areas": [],
        "eurovoc_concepts": [],
        "responsible_committee": None,
        "related": [],
        "sources": [
            {
                "accessed_at": "2023-01-01T12:00:00",
                "name": "Results of roll-call votes (XML)",
                "url": "https://europarl.europa.eu/vote-results.xml",
            },
        ],
    }

    assert res.json == expected


def test_votes_api_csv(records, api):
    res = api.get("/api/votes/1.csv")
    assert res.headers["Content-Type"] == "text/csv"

    expected = (
        "position,member.id,member.first_name,member.last_name,member.country.code,member.country.label,member.country.iso_alpha_2,member.group.code,member.group.label,member.group.short_label\r\n"
        "VotePosition.FOR,1,John,Doe,FRA,France,FR,GUE_NGL,The Left in the European Parliament – GUE/NGL,GUE/NGL\r\n"
        "VotePosition.AGAINST,2,Jane,Smith,DEU,Germany,DE,EPP,European People’s Party,EPP\r\n"
    )

    assert res.text == expected


def test_votes_api_related_votes(db_session, api):
    member = Member(
        id=1,
        first_name="Jane",
        last_name="Smith",
        country=Country["DEU"],
        terms=[9],
        group_memberships=[
            GroupMembership(
                term=9,
                start_date=datetime.date(2023, 1, 1),
                end_date=datetime.date(2023, 12, 31),
                group=Group["EPP"],
            ),
        ],
    )

    amendment = Vote(
        id=1,
        timestamp=datetime.datetime(2023, 1, 1, 0, 0, 0),
        order=1,
        title="Should we have pizza for lunch?",
        description="Am 1",
        group_key="abc123",
        member_votes=[
            MemberVote(
                web_id=1,
                position=VotePosition.FOR,
            ),
        ],
    )

    main_vote = Vote(
        id=2,
        timestamp=datetime.datetime(2023, 1, 1, 0, 0, 0),
        order=2,
        title="Should we have pizza for lunch?",
        description="Resolution (text as a whole)",
        group_key="abc123",
        member_votes=[
            MemberVote(
                web_id=1,
                position=VotePosition.FOR,
            ),
        ],
    )

    db_session.add_all([member, amendment, main_vote])
    db_session.commit()

    res = api.get("/api/votes/1")

    expected = [
        {
            "id": 1,
            "timestamp": "2023-01-01T00:00:00",
            "description": "Am 1",
        },
        {
            "id": 2,
            "timestamp": "2023-01-01T00:00:00",
            "description": "Resolution (text as a whole)",
        },
    ]

    assert res.json["related"] == expected


def test_votes_api_not_found(api):
    res = api.get("/api/votes/123")

    assert res.status_code == 404
    assert res.json["error"].startswith("404 Not Found")
