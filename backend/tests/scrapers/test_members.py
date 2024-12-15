from datetime import date
from pathlib import Path

from howtheyvote.scrapers import MemberGroupsScraper, MemberInfoScraper, MembersScraper

from .helpers import load_fixture

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


def test_members_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/meps/en/directory/xml/?leg=9",
        body=load_fixture("members/members_directory_term_9.xml"),
    )

    scraper = MembersScraper(term=9)
    fragments = scraper.run()

    assert len(fragments) == 875
    assert fragments[0].group_key == 197490
    assert fragments[0].data.get("term") == 9
    assert fragments[1].group_key == 189525
    assert fragments[1].data.get("term") == 9


def test_member_info_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/meps/en/124834/NAME/home",
        body=load_fixture("members/member_info_sonneborn_home.html"),
    )

    scraper = MemberInfoScraper(web_id=124834)
    fragment = scraper.run()

    assert fragment.data.get("first_name") == "Martin"
    assert fragment.data.get("last_name") == "SONNEBORN"
    assert fragment.data.get("date_of_birth") == date(1965, 5, 15)
    assert fragment.data.get("country") == "DEU"
    assert (
        fragment.data.get("facebook")
        == "https://www.facebook.com/Martin-Sonneborn-178442508884215"
    )
    assert fragment.data.get("twitter") == "https://twitter.com/MartinSonneborn"
    assert fragment.data.get("email") == "martin.sonneborn@europarl.europa.eu"


def test_member_info_scraper_date_of_birth_without(responses):
    responses.get(
        "https://www.europarl.europa.eu/meps/en/124831/NAME/home",
        body=load_fixture("members/member_info_adinolfi_home.html"),
    )

    scraper = MemberInfoScraper(web_id=124831)
    fragment = scraper.run()
    assert fragment.data.get("date_of_birth") is None


def test_member_info_scraper_multiple_emails(responses):
    responses.get(
        "https://www.europarl.europa.eu/meps/en/28229/NAME/home",
        body=load_fixture("members/member_info_weber_home.html"),
    )

    scraper = MemberInfoScraper(web_id=28229)
    fragment = scraper.run()
    assert fragment.data.get("email") == "manfred.weber@europarl.europa.eu"


def test_member_info_scraper_no_social_media(responses):
    responses.get(
        "https://www.europarl.europa.eu/meps/en/124831/NAME/home",
        body=load_fixture("members/member_info_adinolfi_home.html"),
    )

    scraper = MemberInfoScraper(web_id=124831)
    fragment = scraper.run()
    assert fragment.data.get("facebook") is None


def test_member_groups_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/meps/en/124831/NAME/history/8",
        body=load_fixture("members/member_groups_adinolfi_term_8.html"),
    )

    scraper = MemberGroupsScraper(web_id=124831, term=8)
    fragment = scraper.run()

    expected = [
        {
            "group": "EFD",
            "term": 8,
            "start_date": date(2014, 7, 1),
            "end_date": date(2014, 10, 15),
        },
        {
            "group": "NI",
            "term": 8,
            "start_date": date(2014, 10, 16),
            "end_date": date(2014, 10, 19),
        },
        {
            "group": "EFD",
            "term": 8,
            "start_date": date(2014, 10, 20),
            "end_date": date(2019, 7, 1),
        },
    ]

    assert fragment.data.get("group_memberships") == expected


def test_member_groups_scraper_ongoing(responses):
    responses.get(
        "https://www.europarl.europa.eu/meps/en/28229/NAME/history/10",
        body=load_fixture("members/member_groups_weber_term_10.html"),
    )

    scraper = MemberGroupsScraper(web_id=28229, term=10)
    fragment = scraper.run()

    expected = [
        {
            "group": "EPP",
            "term": 10,
            "start_date": date(2024, 7, 16),
            "end_date": None,
        },
    ]

    assert fragment.data.get("group_memberships") == expected
