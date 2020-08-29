import pytest
from requests_mock import ANY
from pathlib import Path
from datetime import date
from math import inf
from bs4 import BeautifulSoup
from ep_votes.scrapers import MembersScraper, MemberInfoScraper
from ep_votes.types import Member, Country, Group, GroupMembership

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


def mock_response(req, context):
    url = req.url.replace("https://europarl.europa.eu", "")

    MOCK_RESPONSES = {
        "/meps/en/directory/xml/?leg=8": "directory_term_8.xml",
        "/meps/en/directory/xml/?leg=9": "directory_term_9.xml",
        "/meps/en/124834/NAME/history/8": "sonneborn_term_8.html",
        "/meps/en/124834/NAME/history/9": "sonneborn_term_9.html",
        "/meps/en/124831/NAME/history/8": "adinolfi_term_8.html",
        "/meps/en/124831/NAME/history/9": "adinolfi_term_9.html",
    }

    file = MOCK_RESPONSES[url]
    path = TEST_DATA_DIR / file

    return Path(path).read_text()


@pytest.fixture
def mock_request(requests_mock):
    requests_mock.get(ANY, text=mock_response)
    yield requests_mock


def test_members_scraper_run(mock_request):
    scraper = MembersScraper()

    expected = [
        Member(terms={8, 9}, europarl_website_id=1),
        Member(terms={9}, europarl_website_id=2),
    ]

    assert scraper.run() == expected


def test_members_scraper_term_url():
    scraper = MembersScraper()
    expected = {
        8: "https://europarl.europa.eu/meps/en/directory/xml/?leg=8",
        9: "https://europarl.europa.eu/meps/en/directory/xml/?leg=9",
    }

    assert scraper._resource_urls() == expected


def test_member_info_scraper_run(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=124834, terms={8, 9})

    expected = Member(
        europarl_website_id=124834,
        terms={8, 9},
        first_name="Martin",
        last_name="SONNEBORN",
        date_of_birth=date(1965, 5, 15),
        country=Country.DE,
    )

    assert scraper.run() == expected


def test_member_info_scraper_profile_url(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=124834, terms={8, 9})
    expected = {
        8: "https://europarl.europa.eu/meps/en/124834/NAME/history/8",
        9: "https://europarl.europa.eu/meps/en/124834/NAME/history/9",
    }

    assert scraper._resource_urls() == expected


def test_member_info_scraper_full_name(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=124834, terms={8, 9})
    scraper._load_resources()
    assert scraper._full_name() == "Martin SONNEBORN"


def test_member_info_scraper_date_of_birth(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=124834, terms={8, 9})
    scraper._load_resources()
    assert scraper._date_of_birth() == date(1965, 5, 15)


def test_member_info_scraper_date_of_birth_without(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=124831, terms={8, 9})
    scraper._load_resources()
    assert scraper._date_of_birth() is None


def test_member_info_scraper_country(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=124834, terms={8, 9})
    scraper._load_resources()
    assert scraper._country() == Country.DE


def test_member_info_scraper_group_memberships(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=124834, terms={8, 9})
    scraper._load_resources()

    expected = [
        GroupMembership(
            group=Group.NI,
            term=8,
            start_date=date(2014, 7, 1),
            end_date=date(2019, 7, 1),
        ),
        GroupMembership(
            group=Group.NI, term=9, start_date=date(2019, 7, 2), end_date=inf
        ),
    ]

    assert scraper._group_memberships() == expected


def test_member_info_scraper_parse_group(mock_request):
    scraper = MemberInfoScraper(europarl_website_id=123, terms={})

    tags = [
        "<strong>02-07-2019 ...</strong> : Renew Europe Group - Member",
        "<strong>02-07-2019 ...</strong> : Non-attached Members",
    ]

    tags = [BeautifulSoup(tag, "lxml") for tag in tags]

    assert scraper._parse_group(tags[0]) == Group.RENEW
    assert scraper._parse_group(tags[1]) == Group.NI
