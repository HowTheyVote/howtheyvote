from pytest import fixture
from unittest.mock import patch
from pathlib import Path
from ep_votes.scrapers import MembersXMLScraper, MemberInfoHTMLScraper
from ep_votes.types import Member

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


@fixture
def members_xml_scraper():
    def mock_download_term(self, term):
        return open(TEST_DATA_DIR / f"directory_term_{term}.xml")

    with patch.object(MembersXMLScraper, "_download_term", new=mock_download_term):
        yield MembersXMLScraper()


def test_members_xml_scraper_run(members_xml_scraper):
    expected = [
        Member(
            first_name="Member",
            last_name="ONE",
            terms={8, 9},
            country=None,
            group=None,
            europarl_website_id=1,
        ),
        Member(
            first_name="Member",
            last_name="TWO",
            terms={9},
            country=None,
            group=None,
            europarl_website_id=2,
        ),
    ]

    assert members_xml_scraper.run() == expected


def test_members_xml_scraper_term_url(members_xml_scraper):
    expected = "https://www.europarl.europa.eu/meps/en/directory/xml/?leg=9"
    assert members_xml_scraper._term_url(term=9) == expected
