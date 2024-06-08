import datetime

import time_machine

from howtheyvote.models import PlenarySession, PlenarySessionLocation


def test_sessions_api(api, db_session):
    past = PlenarySession(
        id="1",
        start_date=datetime.date(2022, 12, 30),
        end_date=datetime.date(2022, 12, 31),
        term=9,
        location=PlenarySessionLocation.SXB,
    )

    current_1 = PlenarySession(
        id="2",
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2023, 1, 4),
        term=9,
        location=PlenarySessionLocation.SXB,
    )

    current_2 = PlenarySession(
        id="3",
        start_date=datetime.date(2023, 1, 1),
        end_date=datetime.date(2023, 1, 1),
        term=9,
        location=PlenarySessionLocation.SXB,
    )

    upcoming = PlenarySession(
        id="4",
        start_date=datetime.date(2023, 1, 2),
        end_date=datetime.date(2023, 1, 4),
        term=9,
        location=PlenarySessionLocation.SXB,
    )

    db_session.add_all([past, current_1, current_2, upcoming])
    db_session.commit()

    with time_machine.travel(datetime.date(2023, 1, 1)):
        response_all = api.get("/api/sessions")
        response_past = api.get("/api/sessions?status=past")
        response_current = api.get("/api/sessions?status=current")
        response_upcoming = api.get("/api/sessions?status=upcoming")

    expected_all = [
        {
            "id": "1",
            "start_date": "2022-12-30",
            "end_date": "2022-12-31",
            "status": "PAST",
            "location": "SXB",
        },
        {
            "id": "2",
            "start_date": "2023-01-01",
            "end_date": "2023-01-04",
            "status": "CURRENT",
            "location": "SXB",
        },
        {
            "id": "3",
            "start_date": "2023-01-01",
            "end_date": "2023-01-01",
            "status": "CURRENT",
            "location": "SXB",
        },
        {
            "id": "4",
            "start_date": "2023-01-02",
            "end_date": "2023-01-04",
            "status": "UPCOMING",
            "location": "SXB",
        },
    ]

    expected_past = [
        {
            "id": "1",
            "start_date": "2022-12-30",
            "end_date": "2022-12-31",
            "status": "PAST",
            "location": "SXB",
        },
    ]

    expected_current = [
        {
            "id": "2",
            "start_date": "2023-01-01",
            "end_date": "2023-01-04",
            "status": "CURRENT",
            "location": "SXB",
        },
        {
            "id": "3",
            "start_date": "2023-01-01",
            "end_date": "2023-01-01",
            "status": "CURRENT",
            "location": "SXB",
        },
    ]

    expected_upcoming = [
        {
            "id": "4",
            "start_date": "2023-01-02",
            "end_date": "2023-01-04",
            "status": "UPCOMING",
            "location": "SXB",
        },
    ]

    assert response_all.json["total"] == 4
    assert response_all.json["results"] == expected_all

    assert response_past.json["total"] == 1
    assert response_past.json["results"] == expected_past

    assert response_current.json["total"] == 2
    assert response_current.json["results"] == expected_current

    assert response_upcoming.json["total"] == 1
    assert response_upcoming.json["results"] == expected_upcoming
