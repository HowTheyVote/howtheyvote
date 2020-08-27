from pytest import fixture
from unittest.mock import patch
from pathlib import Path
from datetime import date
from ep_votes.scrapers import MembersXMLScraper, MemberInfoHTMLScraper
from ep_votes.types import Member, Country

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


@fixture
def member():
    return Member(europarl_website_id=124834, terms={8, 9})


@fixture
def members_xml_scraper():
    def mock_download_term(self, term):
        return open(TEST_DATA_DIR / f"directory_term_{term}.xml")

    with patch.object(MembersXMLScraper, "_download_term", new=mock_download_term):
        yield MembersXMLScraper()


@fixture
def member_info_html_scraper(member):
    def mock_download_term(self, term):
        return Path(TEST_DATA_DIR / f"sonneborn_term_{term}.html").read_text()

    with patch.object(MemberInfoHTMLScraper, "_download_term", new=mock_download_term):
        yield MemberInfoHTMLScraper(member=member)


def test_members_xml_scraper_run(members_xml_scraper):
    expected = [
        Member(terms={8, 9}, europarl_website_id=1),
        Member(terms={9}, europarl_website_id=2),
    ]

    assert members_xml_scraper.run() == expected


def test_members_xml_scraper_term_url(members_xml_scraper):
    expected = "https://www.europarl.europa.eu/meps/en/directory/xml/?leg=9"
    assert members_xml_scraper._term_url(term=9) == expected


def test_member_info_html_scraper_run(member_info_html_scraper):
    expected = Member(
        europarl_website_id=124834,
        terms={8, 9},
        first_name="Martin",
        last_name="SONNEBORN",
        date_of_birth=date(1965, 5, 15),
        country=Country.DE,
    )

    assert member_info_html_scraper.run() == expected


def test_member_info_html_scraper_profile_url(member_info_html_scraper):
    expected = "https://europarl.europa.eu/meps/en/124834/NAME/history/9"
    assert member_info_html_scraper._profile_url(term=9) == expected


def test_member_info_html_scraper_full_name(member_info_html_scraper):
    member_info_html_scraper._download()
    assert member_info_html_scraper._full_name() == "Martin SONNEBORN"


def test_member_info_html_scraper_date_of_birth(member_info_html_scraper):
    member_info_html_scraper._download()
    assert member_info_html_scraper._date_of_birth() == date(1965, 5, 15)


def test_member_info_html_scraper_country(member_info_html_scraper):
    member_info_html_scraper._download()
    assert member_info_html_scraper._country() == Country.DE
