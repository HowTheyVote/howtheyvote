import datetime

from bs4 import BeautifulSoup

from howtheyvote.scrapers.oeil_summaries import (
    OEILSummaryIDScraper,
    OEILSummaryScraper,
)

from ..helpers import load_fixture


def test_oeil_summary_id_scraper_run(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2021/2540(RSP)",
        body=load_fixture(
            "scrapers/data/oeil_summaries/oeil-procedure-file_2021-2540-rsp.html"
        ),
    )

    scraper = OEILSummaryIDScraper(
        day_of_vote=datetime.date(2021, 2, 11),
        procedure_reference="2021/2540(RSP)",
    )
    fragments = list(scraper.run())
    assert fragments[0].model == "OEILSummary"
    assert fragments[0].group_key == 1651118
    assert fragments[0].data == {
        "id": 1651118,
        "date": datetime.date(2021, 2, 11),
        "procedure_reference": "2021/2540(RSP)",
    }


def test_oeil_summary_id_scraper_run_no_summary(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2020/2042(INI)",
        body=load_fixture(
            "scrapers/data/oeil_summaries/oeil-procedure-file_2020-2042-ini.html"
        ),
    )

    scraper = OEILSummaryIDScraper(
        day_of_vote=datetime.date(2021, 5, 19),
        procedure_reference="2020/2042(INI)",
    )
    assert list(scraper.run()) == []


def test_oeil_summary_scraper(responses):
    responses.get(
        "https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1651118",
        body=load_fixture("scrapers/data/oeil_summaries/oeil-document-summary_1651118.html"),
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
        body=load_fixture("scrapers/data/oeil_summaries/oeil-document-summary_1864147.html"),
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
