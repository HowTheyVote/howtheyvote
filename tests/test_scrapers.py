from pytest import fixture
from unittest.mock import patch
from pathlib import Path
from ep_votes.scrapers import MembersXMLScraper
from ep_votes.member import Member
from ep_votes.group import Group
from ep_votes.country import Country

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


@fixture
def members_xml_scraper():
    with patch("ep_votes.scrapers.MembersXMLScraper._download_xml") as mock_method:
        mock_method.return_value = open(TEST_DATA_DIR / "current_members.xml")
        yield MembersXMLScraper()


def test_members_xml_scraper_run(members_xml_scraper):
    expected = [
        Member(
            first_name="Magdalena",
            last_name="ADAMOWICZ",
            country=Country.PL,
            group=Group.EPP,
            europarl_website_id=197490,
        ),
        Member(
            first_name="Asim",
            last_name="ADEMOV",
            country=Country.BG,
            group=Group.EPP,
            europarl_website_id=189525,
        ),
    ]

    assert members_xml_scraper.run() == expected
