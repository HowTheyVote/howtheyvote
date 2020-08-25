import pytest
import json
from pathlib import Path
from ep_votes.members_xml_scraper import MembersXMLScraper
from ep_votes.member import Member
from ep_votes.group import Group
from ep_votes.country import Country

TEST_DATA_DIR = Path(__file__).resolve().parent / 'data'

@pytest.fixture()
def scraper():
    return MembersXMLScraper()

def test_get_members(scraper):
    scraper._input = open(TEST_DATA_DIR / 'current_meps.xml')
    scraper._parse_input()

    expected = [
        Member(first_name='Magdalena', last_name='ADAMOWICZ', country=Country.PL, group=Group.EPP, term=9, europarl_website_id=197490),
        Member(first_name='Asim', last_name='ADEMOV', country=Country.BG, group=Group.EPP, term=9, europarl_website_id=189525),
    ]

    assert scraper.get_members() == expected
