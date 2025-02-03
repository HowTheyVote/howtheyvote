import datetime

from howtheyvote.scrapers import PressReleaseScraper

from ..helpers import load_fixture


def test_press_release_scraper(responses):
    responses.get(
        "https://www.europarl.europa.eu/news/en/press-room/20221014IPR43206",
        body=load_fixture("scrapers/data/press_releases/press-release_20221014IPR43206.html"),
    )

    scraper = PressReleaseScraper(release_id="20221014IPR43206")
    fragment = scraper.run()

    assert fragment.group_key == "20221014IPR43206"
    assert (
        fragment.data.get("title")
        == "Car-recharging stations should be available every 60 km, say MEPs"
    )
    assert fragment.data.get("published_at") == datetime.datetime(2022, 10, 19, 13, 14, 0)
    assert fragment.data.get("reference") == ["A9-0234/2022", "A9-0233/2022"]
    assert fragment.data.get("procedure_reference") == ["2021/0223(COD)", "2021/0210(COD)"]
    assert (
        fragment.data.get("facts")
        == "<ul><li>Faster roll-out of recharging stations needed on main EU roads</li><li>Easy to use and affordable recharging/refuelling</li><li>Fewer emissions in the maritime sector</li></ul>"
    )


def test_press_release_scraper_new_procedure_urls(responses):
    responses.get(
        "https://www.europarl.europa.eu/news/en/press-room/20241212IPR25960",
        body=load_fixture("scrapers/data/press_releases/press-release_20241212IPR25960.html"),
    )

    scraper = PressReleaseScraper(release_id="20241212IPR25960")
    fragment = scraper.run()
    assert fragment.data.get("procedure_reference") == ["2024/0275(COD)", "2024/0274(COD)"]
