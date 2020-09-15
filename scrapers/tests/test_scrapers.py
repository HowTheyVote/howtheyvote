import pytest
from requests_mock import ANY
from pathlib import Path
from datetime import date, datetime
from bs4 import BeautifulSoup
from ep_votes.scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VoteResultsScraper,
    DocumentInfoScraper,
)
from ep_votes.models import (
    Member,
    MemberInfo,
    Country,
    Group,
    GroupMembership,
    Position,
    Voting,
    Vote,
    Doc,
    DocReference,
    DocType,
)

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


def mock_response(req, context):
    url = req.url.replace("https://europarl.europa.eu", "")

    MOCK_RESPONSES = {
        "/meps/en/directory/xml/?leg=8": "directory_term_8.xml",
        "/meps/en/directory/xml/?leg=9": "directory_term_9.xml",
        "/meps/en/124834/NAME/home": "sonneborn_home.html",
        "/meps/en/124834/NAME/history/8": "sonneborn_term_8.html",
        "/meps/en/124834/NAME/history/9": "sonneborn_term_9.html",
        "/meps/en/124831/NAME/home": "adinolfi_home.html",
        "/meps/en/124831/NAME/history/8": "adinolfi_term_8.html",
        "/meps/en/124831/NAME/history/9": "adinolfi_term_9.html",
        "/doceo/document/PV-9-2020-07-23-RCV_FR.xml": "pv-9-2020-07-23-rcv-fr.xml",
        "/doceo/document/B-9-2020-0220_EN.html": "b-9-2020-0220-en.html",
    }

    file = MOCK_RESPONSES[url]
    path = TEST_DATA_DIR / file

    return Path(path).read_text()


@pytest.fixture
def mock_request(requests_mock):
    requests_mock.get(ANY, text=mock_response)
    yield requests_mock


def test_members_scraper_run(mock_request):
    scraper = MembersScraper(term=9)

    expected = [
        Member(terms=[9], web_id=1),
        Member(terms=[9], web_id=2),
    ]

    assert scraper.run() == expected


def test_member_info_scraper_run(mock_request):
    scraper = MemberInfoScraper(web_id=124834)

    expected = MemberInfo(
        first_name="Martin",
        last_name="SONNEBORN",
        date_of_birth=date(1965, 5, 15),
        country=Country.DE,
    )

    assert scraper.run() == expected


def test_member_info_scraper_date_of_birth_without(mock_request):
    scraper = MemberInfoScraper(web_id=124831)
    scraper._load()
    assert scraper._date_of_birth() is None


def test_member_groups_scraper_run(mock_request):
    scraper = MemberGroupsScraper(web_id=124834, term=8)

    expected = [
        GroupMembership(
            group=Group.NI,
            term=8,
            start_date=date(2014, 7, 1),
            end_date=date(2019, 7, 1),
        ),
    ]

    assert scraper.run() == expected


def test_member_groups_scraper_date_range(mock_request):
    scraper = MemberGroupsScraper(web_id=123, term=8)

    tags = [
        "<strong>01-07-2014 / 01-07-2019</strong> : Group XYZ",
        "<strong>02-07-2019 ...</strong> : Group XYZ",
    ]

    tags = [BeautifulSoup(tag, "lxml").body for tag in tags]

    assert scraper._date_range(tags[0]) == (date(2014, 7, 1), date(2019, 7, 1))
    assert scraper._date_range(tags[1]) == (date(2019, 7, 2), None)


def test_member_groups_scraper_group(mock_request):
    scraper = MemberGroupsScraper(web_id=123, term=8)

    tags = [
        "<strong>02-07-2019 ...</strong> : Renew Europe Group - Member",
        "<strong>02-07-2019 ...</strong> : Group of the European People's Party (Christian Democrats) - Chair",  # noqa: E501
        "<strong>02-07-2019 ...</strong> : Group of the European United Left - Nordic Green Left - Co-Chair",  # noqa: E501
        "<strong>02-07-2019 ...</strong> : Group of the Greens/European Free Alliance - Vice-Chair",  # noqa: E501
        "<strong>02-07-2019 ...</strong> : Non-attached Members",
    ]

    tags = [BeautifulSoup(tag, "lxml").body for tag in tags]

    assert scraper._group(tags[0]) == Group.RENEW
    assert scraper._group(tags[1]) == Group.EPP
    assert scraper._group(tags[2]) == Group.GUE
    assert scraper._group(tags[3]) == Group.GREENS
    assert scraper._group(tags[4]) == Group.NI


def test_vote_results_scraper_run(mock_request):
    scraper = VoteResultsScraper(term=9, date=date(2020, 7, 23))

    votings = [
        Voting(doceo_member_id=7244, name="Aguilar", position=Position.FOR),
        Voting(doceo_member_id=6630, name="de Graaff", position=Position.AGAINST),
        Voting(doceo_member_id=6836, name="Kolakušić", position=Position.ABSTENTION),
    ]

    vote = [
        Vote(
            doceo_vote_id=116365,
            date=datetime(2020, 7, 23, 12, 49, 32),
            description="§ 1/1",
            reference=DocReference(type=DocType.B, term=9, number=229, year=2020),
            votings=votings,
        )
    ]

    assert scraper.run() == vote


@pytest.fixture
def description_tags():
    descriptions = [
        (
            "<RollCallVote.Description.Text>"
            "<a>B9-0229/2020</a> - § 1/1"
            "</RollCallVote.Description.Text>"
        ),
        (
            "<RollCallVote.Description.Text>"
            "Ordre du jour de mardi - demande du groupe GUE/NGL"
            "</RollCallVote.Description.Text>"
        ),
    ]

    return [BeautifulSoup(desc, "lxml-xml") for desc in descriptions]


def test_vote_results_scraper_description(description_tags):
    scraper = VoteResultsScraper(term=9, date=date(2020, 7, 23))

    expected = [
        "§ 1/1",
        "Ordre du jour de mardi - demande du groupe GUE/NGL",
    ]

    assert scraper._description(description_tags[0]) == expected[0]
    assert scraper._description(description_tags[1]) == expected[1]


def test_vote_results_scraper_reference(description_tags):
    scraper = VoteResultsScraper(term=9, date=date(2020, 7, 23))

    expected = [DocReference.from_str("B9-0229/2020"), None]

    assert scraper._reference(description_tags[0]) == expected[0]
    assert scraper._reference(description_tags[1]) == expected[1]


def test_document_scraper_run(mock_request):
    title = "MOTION FOR A RESOLUTION on the EU’s public health strategy post-COVID-19"

    scraper = DocumentInfoScraper(
        type=DocType.B,
        term=9,
        number=220,
        year=2020,
    )

    expected = Doc(title=title)

    assert scraper.run() == expected
