import datetime

import time_machine

from howtheyvote.models import Country, Group, GroupMembership, Member


def test_members_api_show(api, db_session):
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

    db_session.add_all([john, jane])
    db_session.commit()

    res = api.get("/api/members/123")
    assert res.status_code == 404

    res = api.get("/api/members/1")
    assert res.status_code == 200
    assert res.json == {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "terms": [9],
        "date_of_birth": None,
        "country": {
            "code": "FRA",
            "iso_alpha_2": "FR",
            "label": "France",
        },
        "group": {
            "code": "GUE_NGL",
            "label": "The Left in the European Parliament",
            "short_label": "The Left",
        },
        "photo_url": "/api/static/members/1.jpg",
        "thumb_url": "/api/static/members/1-104.jpg",
        "sharepic_url": "/api/static/members/sharepic-1.png",
        "email": None,
        "facebook": None,
        "twitter": None,
    }

    with time_machine.travel("2022-02-01"):
        res = api.get("/api/members/1")
        assert res.status_code == 200
        assert res.json["group"] == {
            "code": "NI",
            "label": "Non-attached Members",
            "short_label": "Non-attached",
        }

    res = api.get("/api/members/2")
    assert res.status_code == 200
    assert res.json["group"] == {
        "code": "EPP",
        "label": "European People’s Party",
        "short_label": "EPP",
    }
