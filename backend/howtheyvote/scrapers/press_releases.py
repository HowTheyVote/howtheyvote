import datetime
import re
from collections.abc import Iterator
from typing import cast
from urllib.parse import parse_qs, urlencode, urlparse

from bs4 import BeautifulSoup
from structlog import get_logger

from ..models import Fragment, PressRelease
from .common import BeautifulSoupScraper, RequestCache

log = get_logger(__name__)


class PressReleasesIndexScraper(BeautifulSoupScraper):
    BASE_URL = "https://www.europarl.europa.eu/news/{language}/page/{page}"
    ITEM_URL = "https://www.europarl.europa.eu/news/en/press-room/"

    def __init__(
        self,
        language: str,
        session_start_date: datetime.date | None = None,
        page: int = 0,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(
            session_start_date=session_start_date,
            language=language,
            page=page,
            request_cache=request_cache,
        )
        self.session_start_date = session_start_date
        self.language = language
        self.page = page
        self.base_url = self.BASE_URL.format(language=self.language, page=self.page)

    def _url(self) -> str:
        query_string = {}

        if self.session_start_date:
            query_string = {
                "contentType": "plenary",
                "keywordValue": self.session_start_date.strftime("%d-%m-%Y"),
            }

        return f"{self.base_url}?{urlencode(query_string)}"

    def _extract_data(self, doc: BeautifulSoup) -> list[Fragment]:
        items = doc.select("article.ep-m_product")
        fragments: list[Fragment] = []

        for item in items:
            # When scraping unfiltered index pages, the list will also contain press releases
            # that are not related to a plenary session. We keep only press releases related to
            # plenary sessions.
            content_type = item.select_one(".ep-layout_contenttype.ep-layout_plenary")

            if not content_type:
                continue

            if not content_type.get_text(strip=True).lower() == "plenary session":
                continue

            link = item.select_one("a")
            href = link["href"] if link else None

            if not isinstance(href, str):
                continue

            if not href.startswith(self.ITEM_URL):
                continue

            regex = re.escape(self.ITEM_URL) + r"(.*)/"
            match = re.match(regex, href)

            if not match:
                log.warning("Could not extract ID, skipping press release", url=href)
                continue

            release_id = match.group(1)

            if not release_id:
                log.warning("Could not extract ID, skipping press release", url=href)
                continue

            fragment = self._fragment(
                model=PressRelease,
                source_id=release_id,
                group_key=release_id,
                data={},
            )

            fragments.append(fragment)

        return fragments


class PressReleasesRSSScraper(BeautifulSoupScraper):
    URL = "https://www.europarl.europa.eu/rss/doc/press-releases-plenary/en.xml"
    BS_PARSER = "lxml-xml"

    def _url(self) -> str:
        return self.URL

    def _extract_data(self, doc: BeautifulSoup) -> list[Fragment]:
        fragments = []

        for item in doc.select("item"):
            link_tag = item.select_one("link")

            if not link_tag:
                continue

            release_id = self._id_from_url(link_tag.text.strip())

            if not release_id:
                continue

            fragment = self._fragment(
                model=PressRelease,
                source_id=release_id,
                group_key=release_id,
                data={},
            )

            fragments.append(fragment)

        return fragments

    def _id_from_url(self, url: str) -> str | None:
        # https://www.europarl.europa.eu/news/en/press-room/20230911IPR04931/
        pattern = r"\d{4}\d{2}\d{2}IPR\d+"
        match = re.search(pattern, url)

        if not match:
            return None

        return match.group(0)


class PressReleaseScraper(BeautifulSoupScraper):
    BASE_URL = "https://www.europarl.europa.eu/news/en/press-room/"

    def __init__(
        self,
        release_id: str,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(release_id=release_id, request_cache=request_cache)
        self.release_id = release_id

    def _url(self) -> str:
        return f"{self.BASE_URL}{self.release_id}"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment | None:
        return self._fragment(
            model=PressRelease,
            source_id=self.release_id,
            group_key=self.release_id,
            data={
                "title": self._title(doc),
                "published_at": self._published_at(doc),
                "reference": self._references(doc),
                "procedure_reference": self._procedure_references(doc),
                "facts": self._facts(doc),
                "text": self._text(doc),
            },
        )

    def _title(self, doc: BeautifulSoup) -> str | None:
        title = doc.select_one("#website-body h1.ep_title")

        if not title:
            return None

        return title.text.strip()

    def _facts(self, doc: BeautifulSoup) -> str | None:
        list_ = doc.select_one("#website-body .ep-a_facts ul")

        if not list_:
            # Some press releases use a standard lists at the beginning of the article body
            list_ = doc.select_one("#website-body .ep-a_text ul")

        if not list_:
            return None

        items = [item.text.strip() for item in list_.select("li")]
        items = [f"<li>{item}</li>" for item in items]
        return "<ul>" + "".join(items) + "</ul>"

    def _text(self, doc: BeautifulSoup) -> str | None:
        paragraphs = doc.select(
            'article[role="main"] :where(.ep-wysiwig_paragraph, .ep-a_text p)'
        )
        text = "\n\n".join(
            [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        )
        return text if text else None

    def _published_at(self, doc: BeautifulSoup) -> datetime.datetime | None:
        element = doc.select_one('.ep_subtitle time[itemprop="datePublished"]')

        if not element:
            return None

        # https://github.com/python/typeshed/issues/8755
        iso_str = cast(str | None, element.get("datetime"))

        if not iso_str:
            return None

        return datetime.datetime.fromisoformat(iso_str)

    def _references(self, doc: BeautifulSoup) -> list[str] | None:
        references: list[str] = []

        for link in self._links(doc):
            url = urlparse(link)

            if not url.path.startswith("/doceo/document"):
                continue

            filename = url.path.rsplit("/", 1)[-1]
            pattern = r"(A|B|RC)-(\d+)-(\d{4})-(\d{4})_EN\.html"
            match = re.match(pattern, filename)

            if not match:
                continue

            type_ = match.group(1)
            term = match.group(2)
            year = match.group(3)
            number = match.group(4)

            if type_ == "RC":
                type_ = "RC-B"

            references.append(f"{type_}{term}-{number}/{year}")

        return references

    def _procedure_references(self, doc: BeautifulSoup) -> list[str] | None:
        references: list[str] = []

        for link in self._links(doc):
            if not link.startswith(
                (
                    "https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do",
                    "https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file",
                )
            ):
                continue

            url = urlparse(link)
            args = parse_qs(url.query)
            ref = args.get("reference")

            if ref:
                # Some press releases link to two or more (related) procedures. We're
                # ignoring this case for the sake of simplicity.
                references.append(ref[0].strip())

        return references

    def _links(self, doc: BeautifulSoup) -> Iterator[str]:
        links = doc.select(".ep-a_links ul li a")

        for link in links:
            href = link.get("href")

            if isinstance(href, str):
                yield href
