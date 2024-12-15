import datetime

import pytest

from howtheyvote.models import Fragment, MemberVote, VotePosition
from howtheyvote.scrapers.common import ScrapingError
from howtheyvote.scrapers.votes import (
    EurlexDocumentScraper,
    EurlexProcedureScraper,
    ProcedureScraper,
    RCVListScraper,
)

from ..helpers import record_to_dict
from .helpers import load_fixture


@pytest.mark.always_mock_requests
def test_rcv_list_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2020-07-23-RCV_FR.xml",
        body=load_fixture("votes/rcv_list_pv-9-2020-07-23-rcv-fr.xml"),
    )

    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2020, 7, 23),
        active_members=[
            (198096, "Mazaly", "AGUILAR"),
            (125025, "Marcel", "de GRAAFF"),
            (197438, "Mislav", "KOLAKUŠIĆ"),
        ],
    )

    actual = scraper.run()

    expected = [
        Fragment(
            model="Vote",
            source_name="RCVListScraper",
            source_id=116365,
            group_key=116365,
            source_url="https://www.europarl.europa.eu/doceo/document/PV-9-2020-07-23-RCV_FR.xml",
            data={
                "timestamp": datetime.datetime(2020, 7, 23, 12, 49, 32),
                "term": 9,
                "title": None,
                "reference": "B9-0229/2020",
                "description": "§ 1/1",
                "rapporteur": None,
                "order": 1,
                "member_votes": [
                    MemberVote(web_id=198096, position=VotePosition.FOR),
                    MemberVote(web_id=125025, position=VotePosition.AGAINST),
                    MemberVote(web_id=197438, position=VotePosition.ABSTENTION),
                ],
            },
        ),
    ]

    assert record_to_dict(actual[0]) == record_to_dict(expected[0])


@pytest.mark.always_mock_requests
def test_rcv_list_scraper_incorrect_totals(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2020-07-23-RCV_FR.xml",
        body=load_fixture("votes/rcv_list_incorrect_pv-9-2020-07-23-rcv-fr.xml"),
    )

    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2020, 7, 23),
        active_members=[
            (198096, "Mazaly", "AGUILAR"),
            (125025, "Marcel", "de GRAAFF"),
            (197438, "Mislav", "KOLAKUŠIĆ"),
        ],
    )

    with pytest.raises(
        ScrapingError, match="Total number of 1 extracted FOR votes does not match expected 2"
    ):
        scraper.run()


@pytest.mark.always_mock_requests
def test_rcv_list_scraper_did_not_vote(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2020-07-23-RCV_FR.xml",
        body=load_fixture("votes/rcv_list_pv-9-2020-07-23-rcv-fr.xml"),
    )

    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2020, 7, 23),
        active_members=[
            (198096, "Mazaly", "AGUILAR"),
            (125025, "Marcel", "de GRAAFF"),
            (197438, "Mislav", "KOLAKUŠIĆ"),
            (123456, "John", "DOE"),
        ],
    )

    actual = scraper.run()[0].data.get("member_votes")

    expected = [
        MemberVote(web_id=198096, position=VotePosition.FOR),
        MemberVote(web_id=125025, position=VotePosition.AGAINST),
        MemberVote(web_id=197438, position=VotePosition.ABSTENTION),
        MemberVote(web_id=123456, position=VotePosition.DID_NOT_VOTE),
    ]

    assert actual == expected


@pytest.mark.always_mock_requests
def test_rcv_list_scraper_same_name(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2020-09-15-RCV_FR.xml",
        body=load_fixture("votes/rcv_list_pv-9-2020-09-15-rcv-fr.xml"),
    )

    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2020, 9, 15),
        active_members=[
            (197826, "Matteo", "ADINOLFI"),
            (124831, "Isabella", "ADINOLFI"),
        ],
    )

    actual = scraper.run()[0].data.get("member_votes")

    expected = [
        MemberVote(web_id=197826, position=VotePosition.FOR),
        MemberVote(web_id=124831, position=VotePosition.FOR),
    ]

    assert actual == expected


@pytest.mark.always_mock_requests
def test_rcv_list_scraper_pers_id(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2023-12-12-RCV_FR.xml",
        body=load_fixture("votes/rcv_list_pv-9-2023-12-12-rcv-fr.xml"),
    )

    # The voting list has a different spelling ("Glueck" instead of "Glück"). Cases like this
    # are no problem anymore as newer RCV lists contain a `PersId` attribute that corresponds
    # with the member IDs from profile pages on the Parliament’s website.
    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2023, 12, 12),
        active_members=[
            (197443, "Andreas", "GLÜCK"),
        ],
    )

    actual = scraper.run()[0].data.get("member_votes")

    expected = [
        MemberVote(web_id=197443, position=VotePosition.FOR),
    ]

    assert actual == expected


@pytest.mark.always_mock_requests
def test_rcv_list_scraper_pers_id_unknown(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2023-12-12-RCV_FR.xml",
        body=load_fixture("votes/rcv_list_pv-9-2023-12-12-rcv-fr.xml"),
    )

    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2023, 12, 12),
        active_members=[],
    )

    with pytest.raises(ScrapingError, match="Could not find member with ID 197443"):
        scraper.run()


@pytest.mark.always_mock_requests
def test_rcv_list_scraper_document_register(responses):
    doceo_mock = responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2020-07-23-RCV_FR.xml",
        status=404,
    )
    register_mock = responses.get(
        "https://www.europarl.europa.eu/RegData/seance_pleniere/proces_verbal/2020/07-23/liste_presence/P9_PV(2020)07-23(RCV)_XC.xml",
        body=load_fixture("votes/rcv_list_p9-pv(2020)07-23(rcv)_xc.xml"),
    )

    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2020, 7, 23),
        active_members=[
            (198096, "Mazaly", "AGUILAR"),
            (125025, "Marcel", "de GRAAF"),
            (197438, "Mislav", "KOLAKUŠIĆ"),
        ],
    )

    actual = scraper.run()

    assert len(actual) == 1
    assert doceo_mock.call_count == 3  # 3 retries
    assert register_mock.call_count == 1


@pytest.mark.always_mock_requests
def test_rcv_list_scraper_timestamp_from_text(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2019-07-15-RCV_FR.xml",
        body=load_fixture("votes/rcv_list_pv-9-2019-07-15-rcv-fr.xml"),
    )

    scraper = RCVListScraper(
        term=9,
        date=datetime.date(2019, 7, 15),
        active_members=[],
    )

    data = scraper.run()[0].data
    assert data.get("timestamp") == datetime.datetime(2019, 7, 15, 17, 9, 37)
    assert data.get("title") == "Mardi - demande du groupe GUE/NGL"
    assert data.get("description") is None


def test_procedure_scraper(responses):
    responses.get(
        "https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference=2023/2019(INI)",
        body=load_fixture("votes/oeil-procedure-file_2023-2019-ini.html"),
    )

    scraper = ProcedureScraper(vote_id=162214, procedure_reference="2023/2019(INI)")
    actual = scraper.run()

    expected = Fragment(
        model="Vote",
        source_name="ProcedureScraper",
        source_id=162214,
        group_key=162214,
        source_url="https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference=2023/2019(INI)",
        data={
            "procedure_title": "Implementation of the 2018 Geoblocking Regulation in the Digital Single Market",
            "geo_areas": [],
        },
    )

    assert record_to_dict(actual) == record_to_dict(expected)


def test_procedure_scraper_geo_areas(responses):
    responses.get(
        "https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference=2022/2852(RSP)",
        body=load_fixture("votes/oeil-procedure-file_2022-2852-rsp.html"),
    )

    scraper = ProcedureScraper(vote_id=149218, procedure_reference="2022/2852(RSP)")
    fragment = scraper.run()
    assert fragment.data["geo_areas"] == ["BGR", "ROU"]


def test_procedure_scraper_geo_areas_fuzzy(responses):
    responses.get(
        "https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference=2022/2201(INI)",
        body=load_fixture("votes/oeil-procedure-file_2022-2201-ini.html"),
    )

    scraper = ProcedureScraper(vote_id=155056, procedure_reference="2022/2201(INI)")
    fragment = scraper.run()
    assert fragment.data["geo_areas"] == ["XKX"]


def test_eurlex_procedure_scraper_eurovoc_concepts(responses):
    responses.get(
        "https://eur-lex.europa.eu/procedure/EN/2021_106",
        body=load_fixture("votes/eurlex-procedure_2021-106.html"),
    )

    scraper = EurlexProcedureScraper(vote_id=166051, procedure_reference="2021/0106(COD)")
    fragment = scraper.run()

    eurovoc_concepts = {
        "1439",
        "3030",
        "3636",
        "4347",
        "5181",
        "5451",
        "5595",
        "5726",
        "7219",
        "7410",
    }
    assert fragment.data["eurovoc_concepts"] == eurovoc_concepts


def test_eurlex_procedure_scraper_geo_areas(responses):
    responses.get(
        "https://eur-lex.europa.eu/procedure/EN/2023_102",
        body=load_fixture("votes/eurlex-procedure_2023-102.html"),
    )

    scraper = EurlexProcedureScraper(vote_id=161383, procedure_reference="2023/0102(NLE)")
    fragment = scraper.run()

    assert fragment.data["eurovoc_concepts"] == {
        "5540",
        "1474",
        "185",
        "5649",
        "210",
        "2901",
        "5640",
        "8439",
    }
    assert fragment.data["geo_areas"] == {"MNE"}


def test_eurlex_document_scraper_eurovoc_concepts(responses):
    responses.get(
        "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=EP:P9_A(2021)0270",
        body=load_fixture("votes/eurlex-document_p9-a-2021-0270.html"),
    )

    scraper = EurlexDocumentScraper(vote_id=136238, reference="A9-0270/2021")
    fragment = scraper.run()

    eurovoc_concepts = {
        "189",
        "341",
        "4491",
        "5158",
        "538",
        "6064",
        "8439",
        "933",
    }
    assert fragment.data["eurovoc_concepts"] == eurovoc_concepts


def test_eurlex_document_scraper_geo_areas(responses):
    responses.get(
        "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=EP:P9_A(2023)0369",
        body=load_fixture("votes/eurlex-document_p9-a-2023-0369.html"),
    )

    scraper = EurlexDocumentScraper(vote_id=136238, reference="A9-0369/2023")
    fragment = scraper.run()

    assert fragment.data["eurovoc_concepts"] == {
        "2300",
        "6541",
        "5540",
        "1474",
        "5649",
        "210",
        "2901",
        "5640",
        "8439",
    }
    assert fragment.data["geo_areas"] == {"MNE"}
