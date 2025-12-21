import datetime

import pytest
from bs4 import BeautifulSoup

from howtheyvote.models import (
    AmendmentAuthorType,
    Fragment,
    MemberVote,
    ProcedureStage,
    VotePosition,
    VoteResult,
)
from howtheyvote.scrapers.common import NoWorkingUrlError, ScrapingError
from howtheyvote.scrapers.votes import (
    DocumentScraper,
    EurlexDocumentScraper,
    EurlexProcedureScraper,
    OEILSummaryIDScraper,
    OEILSummaryScraper,
    ProcedureScraper,
    RCVListScraper,
    VOTListScraper,
)

from ..helpers import load_fixture, record_to_dict


@pytest.mark.always_mock_requests
def test_rcv_list_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2020-07-23-RCV_FR.xml",
        body=load_fixture("scrapers/data/votes/rcv_list_pv-9-2020-07-23-rcv-fr.xml"),
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
        body=load_fixture("scrapers/data/votes/rcv_list_incorrect_pv-9-2020-07-23-rcv-fr.xml"),
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
        body=load_fixture("scrapers/data/votes/rcv_list_pv-9-2020-07-23-rcv-fr.xml"),
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
        body=load_fixture("scrapers/data/votes/rcv_list_pv-9-2020-09-15-rcv-fr.xml"),
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
        body=load_fixture("scrapers/data/votes/rcv_list_pv-9-2023-12-12-rcv-fr.xml"),
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
        body=load_fixture("scrapers/data/votes/rcv_list_pv-9-2023-12-12-rcv-fr.xml"),
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
        body=load_fixture("scrapers/data/votes/rcv_list_p9-pv(2020)07-23(rcv)_xc.xml"),
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
        body=load_fixture("scrapers/data/votes/rcv_list_pv-9-2019-07-15-rcv-fr.xml"),
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


def test_vot_list_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-10-2024-11-28-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-10-2024-11-28-vot-en.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2024, 11, 28), term=10)
    votes = list(scraper.run())

    assert len(votes) == 57
    assert votes[0].source_id == "170875"
    assert votes[0].group_key == "170875"
    assert votes[0].data == {
        "dlv_title": "Hong Kong, notably the cases of Jimmy Lai and the 45 activists recently convicted under the national security law",
        "result": VoteResult.ADOPTED,
        "timestamp": "2024-11-28T12:13:21",
        "procedure_stage": None,
        "amendment_subject": None,
        "amendment_number": None,
        "amendment_authors": None,
    }


@pytest.mark.always_mock_requests
def test_vot_list_scraper_french(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-10-2025-05-22-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-10-2025-05-22-vot-fr.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2025, 5, 22), term=10)

    with pytest.raises(NoWorkingUrlError):
        list(scraper.run())


def test_vot_list_scraper_skip_non_rcv(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-10-2024-11-28-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-10-2024-11-28-vot-en.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2024, 11, 28), term=10)
    votes = list(scraper.run())
    assert len(votes) == 57


def test_vot_list_scraper_skip_lapsed(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-24-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-9-2024-04-24-vot-en.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2024, 4, 24), term=9)
    votes = list(scraper.run())
    assert len(votes) == 116


def test_vot_list_scraper_skip_withdrawn(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-10-2024-11-14-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-10-2024-11-14-vot-en.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2024, 11, 14), term=10)
    votes = list(scraper.run())
    assert len(votes) == 36


def test_vot_list_scraper_procedure_stage(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-10-2024-11-27-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-10-2024-11-27-vot-en.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2024, 11, 27), term=10)
    votes = list(scraper.run())
    assert votes[5].group_key == "170611"
    assert votes[5].data["procedure_stage"] is None
    assert votes[6].group_key == "170671"
    assert votes[6].data["procedure_stage"] == ProcedureStage.OLP_FIRST_READING


def test_vot_list_scraper_skip_info(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-10-2025-05-08-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-10-2025-05-08-vot-en.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2025, 5, 8), term=10)
    votes = list(scraper.run())
    assert len(votes) == 103


def test_vot_list_scraper_amendment_info(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-10-2024-11-28-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-10-2024-11-28-vot-en.xml"),
    )

    scraper = VOTListScraper(date=datetime.date(2024, 11, 28), term=10)
    votes = list(scraper.run())

    assert votes[1].group_key == "170870"
    assert votes[1].data["amendment_subject"] == "§ 1"
    assert votes[1].data["amendment_number"] == "1"
    assert votes[1].data["amendment_authors"] == [
        {"type": AmendmentAuthorType.GROUP, "group": "PFE"},
    ]


def test_vot_list_scraper_multiple_amendment_authors_newline(responses):
    # Multiple authors separated by a newline
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-23-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-9-2024-04-23-vot-en.xml"),
    )
    scraper = VOTListScraper(date=datetime.date(2024, 4, 23), term=9)
    votes = list(scraper.run())

    assert votes[18].group_key == "168601"
    assert votes[18].data["amendment_authors"] == [
        {"type": AmendmentAuthorType.GROUP, "group": "EPP"},
        {"type": AmendmentAuthorType.MEMBERS},
    ]

    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-04-24-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-9-2024-04-24-vot-en.xml"),
    )
    scraper = VOTListScraper(date=datetime.date(2024, 4, 24), term=9)
    votes = list(scraper.run())

    assert votes[5].group_key == "168840"
    assert votes[5].data["amendment_authors"] == [
        {"type": AmendmentAuthorType.COMMITTEE, "committee": None},
        {"type": AmendmentAuthorType.GROUP, "group": "EPP"},
    ]


def test_vot_list_scraper_multiple_amendment_authors_comma(responses):
    # Multiple authors separated by a comma
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-01-15-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-9-2024-01-15-vot-en.xml"),
    )
    scraper = VOTListScraper(date=datetime.date(2024, 1, 15), term=9)
    votes = list(scraper.run())

    assert votes[3].group_key == "163202"
    assert votes[3].data["amendment_authors"] == [
        {"type": AmendmentAuthorType.GROUP, "group": "EPP"},
        {"type": AmendmentAuthorType.GROUP, "group": "SD"},
        {"type": AmendmentAuthorType.GROUP, "group": "RENEW"},
        {"type": AmendmentAuthorType.GROUP, "group": "GREEN_EFA"},
    ]


def test_vot_list_scraper_multiple_amendment_authors_space(responses):
    # Multiple amendment authors separated by a space
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-03-12-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-9-2024-03-12-vot-en.xml"),
    )
    scraper = VOTListScraper(date=datetime.date(2024, 3, 12), term=9)
    votes = list(scraper.run())

    assert votes[11].group_key == "166284"
    assert votes[11].data["amendment_authors"] == [
        {"type": AmendmentAuthorType.GROUP, "group": "GREEN_EFA"},
        {"type": AmendmentAuthorType.MEMBERS},
    ]

    responses.get(
        "https://www.europarl.europa.eu/doceo/document/PV-9-2024-03-14-VOT_EN.xml",
        body=load_fixture("scrapers/data/votes/vot-list_pv-9-2024-03-14-vot-en.xml"),
    )
    scraper = VOTListScraper(date=datetime.date(2024, 3, 14), term=9)
    votes = list(scraper.run())

    assert votes[1].group_key == "166747"
    assert votes[1].data["amendment_authors"] == [
        {"type": AmendmentAuthorType.GROUP, "group": "RENEW"},
        {"type": AmendmentAuthorType.GROUP, "group": "GUE_NGL"},
        {"type": AmendmentAuthorType.MEMBERS},
    ]


def test_procedure_scraper(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2023/2019(INI)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2023-2019-ini.html"),
    )

    scraper = ProcedureScraper(
        vote_id=162214, procedure_reference="2023/2019(INI)", reference=None
    )
    actual = scraper.run()

    expected = Fragment(
        model="Vote",
        source_name="ProcedureScraper",
        source_id=162214,
        group_key=162214,
        source_url="https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2023/2019(INI)",
        data={
            "procedure_reference": "2023/2019(INI)",
            "procedure_title": "Implementation of the 2018 Geoblocking Regulation in the Digital Single Market",
            "geo_areas": [],
            "oeil_subjects": ["2", "3.30.25", "3.45.05", "3.50.15", "4.60.06"],
            "responsible_committees": {"IMCO"},
        },
    )

    assert record_to_dict(actual) == record_to_dict(expected)


def test_procedure_scraper_fallback_document_reference(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=A9-0335/2023",
        status=301,
        headers={
            "Location": "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2023/2019(INI)"
        },
    )
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2023/2019(INI)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2023-2019-ini.html"),
    )

    scraper = ProcedureScraper(
        vote_id=162214, procedure_reference=None, reference="A9-0335/2023"
    )
    actual = scraper.run()

    expected = Fragment(
        model="Vote",
        source_name="ProcedureScraper",
        source_id=162214,
        group_key=162214,
        source_url="https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2023/2019(INI)",
        data={
            "procedure_reference": "2023/2019(INI)",
            "procedure_title": "Implementation of the 2018 Geoblocking Regulation in the Digital Single Market",
            "geo_areas": [],
            "oeil_subjects": ["2", "3.30.25", "3.45.05", "3.50.15", "4.60.06"],
            "responsible_committees": {"IMCO"},
        },
    )

    assert record_to_dict(actual) == record_to_dict(expected)


def test_procedure_scraper_geo_areas(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2022/2852(RSP)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2022-2852-rsp.html"),
    )

    scraper = ProcedureScraper(
        vote_id=149218, procedure_reference="2022/2852(RSP)", reference=None
    )
    fragment = scraper.run()
    assert fragment.data["geo_areas"] == ["BGR", "ROU"]


def test_procedure_scraper_geo_areas_fuzzy(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2022/2201(INI)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2022-2201-ini.html"),
    )

    scraper = ProcedureScraper(
        vote_id=155056, procedure_reference="2022/2201(INI)", reference=None
    )
    fragment = scraper.run()
    assert fragment.data["geo_areas"] == ["XKX"]


def test_procedure_scraper_multiple_responsible_committees(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2024/0258(COD)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2024-0258-cod.html"),
    )

    scraper = ProcedureScraper(
        vote_id=172102, procedure_reference="2024/0258(COD)", reference=None
    )
    fragment = scraper.run()
    assert fragment.data["responsible_committees"] == {"AFET", "BUDG"}


def test_procedure_scraper_apostrophization(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2022/0377(NLE)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2022_0377-nle.html"),
    )

    scraper = ProcedureScraper(
        vote_id=155030, procedure_reference="2022/0377(NLE)", reference=None
    )
    fragment = scraper.run()
    assert fragment.data["procedure_title"] == (
        "EU/Brazil Agreement: modification of concessions"
        " on all the tariff rate quotas included in"
        " the EU Schedule CLXXV as a consequence of"
        " the United Kingdom’s withdrawal from the European Union"
    )


def test_procedure_scraper_non_breaking_spaces(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2025/0229(NLE)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2025_0229-nle.html"),
    )

    scraper = ProcedureScraper(
        vote_id=182462, procedure_reference="2025/0229(NLE)", reference=None
    )
    fragment = scraper.run()
    assert (
        fragment.data["procedure_title"]
        == "European High Performance Computing Joint Undertaking (EuroHPC)"
    )


def test_eurlex_procedure_scraper_eurovoc_concepts(responses):
    responses.get(
        "https://eur-lex.europa.eu/procedure/EN/2021_106",
        body=load_fixture("scrapers/data/votes/eurlex-procedure_2021-106.html"),
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
        body=load_fixture("scrapers/data/votes/eurlex-procedure_2023-102.html"),
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
        body=load_fixture("scrapers/data/votes/eurlex-document_p9-a-2021-0270.html"),
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
        body=load_fixture("scrapers/data/votes/eurlex-document_p9-a-2023-0369.html"),
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


def test_document_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/doceo/document/RC-10-2025-0249_EN.html",
        body=load_fixture("scrapers/data/votes/document_rc-10-2025-0249-en.html"),
    )

    scraper = DocumentScraper(vote_id=176309, reference="RC-B10-0249/2025")
    fragment = scraper.run()

    assert fragment.data == {
        "procedure_reference": "2025/2691(RSP)",
        "texts_adopted_reference": "P10_TA(2025)0096",
    }


def test_oeil_summary_id_scraper_run(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2021/2540(RSP)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2021-2540-rsp.html"),
    )

    scraper = OEILSummaryIDScraper(
        vote_id=127974,
        day_of_vote=datetime.date(2021, 2, 11),
        reference="A9-0115/2021",
        procedure_reference="2021/2540(RSP)",
    )
    fragment = scraper.run()
    assert fragment.group_key == 127974
    assert fragment.data == {"oeil_summary_id": "1651118"}


def test_oeil_summary_id_scraper_run_no_summary(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2020/2042(INI)",
        body=load_fixture("scrapers/data/votes/oeil-procedure-file_2021-2540-rsp.html"),
    )

    scraper = OEILSummaryIDScraper(
        vote_id=131503,
        day_of_vote=datetime.date(2021, 5, 19),
        reference="A9-0115/2021",
        procedure_reference="2020/2042(INI)",
    )
    assert scraper.run() is None


def test_oeil_summary_scraper(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1651118",
        body=load_fixture("scrapers/data/votes/oeil-document-summary_1651118.html"),
    )

    scraper = OEILSummaryScraper(summary_id=1651118)
    fragment = scraper.run()
    assert fragment.group_key == 1651118
    assert fragment.data["content"].startswith(
        "<p>The European Parliament adopted by 667 votes to 1, with 27 abstentions, a resolution on the situation in Myanmar.</p>"
    )


def test_oeil_summary_scraper_headings(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1864147",
        body=load_fixture("scrapers/data/votes/oeil-document-summary_1864147.html"),
    )

    scraper = OEILSummaryScraper(summary_id=1864147)
    fragment = scraper.run()
    assert fragment.group_key == 1864147

    doc = BeautifulSoup(fragment.data["content"])
    headings = [heading.get_text() for heading in doc.select("h2")]
    assert headings == [
        "Significant presence",
        "Structure of a BEFIT group",
        "Calculation of the preliminary tax result",
        "Limitation of royalties, entertainment costs",
        "Controlled foreign companies",
        "Accelerated depreciation rules",
        "Tax incentives",
        "Transitional allocation rule",
        "One-stop shop",
    ]
