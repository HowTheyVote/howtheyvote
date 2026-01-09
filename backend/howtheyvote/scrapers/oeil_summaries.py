import html
import re
from collections.abc import Iterator
from datetime import date
from typing import cast

from bs4 import BeautifulSoup, Tag

from ..models import Fragment, OEILSummary
from .common import BeautifulSoupScraper, RequestCache, ScrapingError


class OEILSummaryIDScraper(BeautifulSoupScraper):
    BASE_URL = "https://oeil.europarl.europa.eu/oeil/en/procedure-file"

    def __init__(
        self,
        day_of_vote: date,
        procedure_reference: str | None,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(request_cache=request_cache)
        self.day_of_vote = day_of_vote
        self.procedure_reference = procedure_reference

    def _url(self) -> str:
        return f"{self.BASE_URL}?reference={self.procedure_reference}"

    def _extract_data(self, doc: BeautifulSoup) -> Iterator[Fragment]:
        section = doc.select_one('.es_product-section:has(h2:-soup-contains("Key events"))')

        if not section:
            return None

        links = section.select(
            "tr"
            + f':has(td:-soup-contains("{self.day_of_vote.strftime("%d/%m/%Y")}"))'
            + ':has(td:-soup-contains("Decision by Parliament")) '
            + 'a:-soup-contains("Summary")'
        )

        if not links:
            return None

        for link in links:
            regex = re.escape("/oeil/en/document-summary?id=") + r"(\d+)"
            href = cast(str, link["href"])
            match = re.search(regex, href)

            if not match:
                return None

            summary_id = int(match.group(1))

            yield self._fragment(
                model=OEILSummary,
                source_id=summary_id,
                group_key=summary_id,
                data={"id": summary_id},
            )


class OEILSummaryScraper(BeautifulSoupScraper):
    BASE_URL = "https://oeil.europarl.europa.eu/oeil/en/document-summary"

    def __init__(
        self,
        summary_id: int,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(request_cache=request_cache)
        self.summary_id = summary_id

    def _url(self) -> str:
        params = f"?id={self.summary_id}"
        return f"{self.BASE_URL}{params}"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment:
        text = doc.select_one(".es_product-content")

        if not text:
            raise ScrapingError

        items = text.select("p.MsoNormal")
        content = "".join([self._normalize_paragraph(item) for item in items])

        return self._fragment(
            model=OEILSummary,
            source_id=self.summary_id,
            group_key=self.summary_id,
            data={"content": content},
        )

    def _normalize_paragraph(self, paragraph: Tag) -> str:
        text = html.escape(paragraph.get_text(strip=True, separator=" ").replace("\n", " "))
        style = paragraph.get("style")

        # Headings aren't marked up using appropriate HTML tags.
        # Instead, they are simply styled using inline CSS.
        if style and "font-weight" in style and "bold" in style:
            return f"<h2>{text}</h2>"

        return f"<p>{text}</p>"
