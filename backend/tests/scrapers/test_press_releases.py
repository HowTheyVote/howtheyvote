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
    assert fragment.data.get("text").startswith(
        "To help the EU become climate neutral, MEPs want car-recharging stations every 60 km, hydrogen refuelling stations every 100 km and fewer emissions from ships."
    )
    assert fragment.data.get("text").endswith(
        "Parliament is now ready to start negotiations with member states."
    )


def test_press_release_scraper_new_procedure_urls(responses):
    responses.get(
        "https://www.europarl.europa.eu/news/en/press-room/20241212IPR25960",
        body=load_fixture("scrapers/data/press_releases/press-release_20241212IPR25960.html"),
    )

    scraper = PressReleaseScraper(release_id="20241212IPR25960")
    fragment = scraper.run()
    assert fragment.data.get("procedure_reference") == ["2024/0275(COD)", "2024/0274(COD)"]


def test_press_releases_scraper_old_text_selector(responses):
    responses.get(
        "https://www.europarl.europa.eu/news/en/press-room/20190712IPR56948",
        body=load_fixture("scrapers/data/press_releases/press-release_20190712IPR56948.html"),
    )

    scraper = PressReleaseScraper(release_id="20190712IPR56948")
    fragment = scraper.run()
    assert fragment.data.get("text").startswith(
        "For the third time this year, the European Parliament adopted a resolution on the situation in Venezuela, expressing its deep concern at the severe state of emergency"
    )
    assert fragment.data.get("text").endswith(
        "Parliament praises the efforts and solidarity shown by neighbouring countries, in particular Colombia, Ecuador and Peru and ask the Commission to continue cooperating with these countries."
    )


def test_press_release_scraper_facts_collapse_lists(responses):
    responses.get(
        "https://www.europarl.europa.eu/news/en/press-room/20201217IPR94207",
        body=load_fixture("scrapers/data/press_releases/press-release_20201217IPR94207.html"),
    )

    scraper = PressReleaseScraper(release_id="20201217IPR94207")
    fragment = scraper.run()

    assert (
        fragment.data.get("facts")
        == "<ul><li>Basic air connectivity: the temporary rules ensuring certain air services between the UK and the EU continue for a maximum of six months were adopted with 680 votes in favour (3 against, 4 abstentions). This includes rights for UK and EU air carriers to continue to fly over and make technical stops on EU territory, as well as serve direct routes to the EU. Also a limited number of specific pandemic-related cargo flights will be allowed.</li><li>Aviation safety: the regulation ensuring various certificates for products, parts, appliances and companies remain valid was adopted with 680 votes in favour (3 against, 4 abstentions). This will avoid UK and EU aircraft that use these products and services being grounded.</li><li>Basic road connectivity: the temporary rules ensuring road freight and road passenger transport for a maximum of six months were adopted with 680 votes in favour (4 against, 3 abstentions). This will allow carriage of goods as well as coach and bus services coming to Europe and going to the UK to continue.</li></ul>"
    )
