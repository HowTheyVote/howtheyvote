import re
from collections.abc import Iterator
from datetime import date, datetime
from typing import cast
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, Tag
from structlog import get_logger

from ..helpers import parse_procedure_reference, parse_reference
from ..models import (
    Committee,
    Country,
    EurovocConcept,
    Fragment,
    MemberVote,
    Vote,
    VotePosition,
)
from .common import BeautifulSoupScraper, RequestCache, ScrapingError
from .helpers import (
    fill_missing_by_reference,
    normalize_name,
    normalize_whitespace,
    parse_rcv_text,
)

log = get_logger(__name__)


class RCVListScraper(BeautifulSoupScraper):
    BASE_URL_EP = "https://www.europarl.europa.eu/doceo/document"
    BASE_URL_DR = "https://www.europarl.europa.eu/RegData/seance_pleniere/proces_verbal"
    BS_PARSER = "lxml-xml"
    RESPONSE_ENCODING = "utf-8"

    # We observed timeouts or even random, intermittent 404 responses for this data
    # source in the past. Retrying a few times usually resolves these issues.
    REQUEST_MAX_RETRIES: int = 2

    # Sometimes alternate names (e.g. compound names) or different spellings
    # are used in voting lists. We use this dict to replace alternate names with the
    # names listed in the MEP profiles on the official website of the Parliament.
    ALTERNATE_NAMES = {
        "Pagazaurtundúa Ruiz": "Pagazaurtundúa",
        "Lechevalier": "Letard-Lechevalier",
        "Gambús": "Gambus Millet",
        "Kozłowska-Rajewicz": "Kozłowska",
        "Aguilera García": "Aguilera",
        "Rodríguez-Piñero Fernández": "Rodríguez-Piñero",
        "Papadakis Konstantinos": "Papadakis",
        "Tomaševski": "Tomaszewski",
        "Figueiredo Nobre De Gusmão": "Gusmão",
        "Benjumea": "Benjumea Benjumea",
        "Zarzalejos Nieto": "Zarzalejos",
        "Maldeikienė": "Seibutytė",
    }

    def __init__(
        self,
        date: date,
        term: int,
        active_members: list[tuple[int, str, str]],
        request_cache: RequestCache | None = None,
    ):
        super().__init__(
            date=date,
            term=term,
            active_members_count=len(active_members),
            request_cache=request_cache,
        )

        self.date = date
        self.term = term
        self.active_member_ids = []
        self.member_ids_by_last_name: dict[str, int] = {}
        self.member_ids_by_full_name: dict[str, int] = {}
        self.member_ids: set[int] = set()

        for member_id, first_name, last_name in active_members:
            last_name = normalize_name(last_name)
            full_name = normalize_name(f"{last_name.lower()} {first_name.lower()}")

            self.active_member_ids.append(member_id)
            self.member_ids_by_last_name[last_name] = member_id
            self.member_ids_by_full_name[full_name] = member_id
            self.member_ids.add(member_id)

    def _url(self) -> list[str]:
        date = self.date.strftime("%Y-%m-%d")
        doceo_url = f"{self.BASE_URL_EP}/PV-{self.term}-{date}-RCV_FR.xml"

        year = self.date.strftime("%Y")
        month = self.date.strftime("%m")
        day = self.date.strftime("%d")
        document_register_url = (
            f"{self.BASE_URL_DR}/{year}/{month}-{day}/liste_presence/"
            f"P{self.term}_PV({year}){month}-{day}(RCV)_XC.xml"
        )

        return [doceo_url, document_register_url]

    def _extract_data(self, doc: BeautifulSoup) -> list[Fragment]:
        tags = doc.find_all("RollCallVote.Result")
        fragments = []

        i = 0

        for tag in tags:
            i += 1
            fragment = self._vote(tag)
            fragment.data["order"] = i
            fragments.append(fragment)

        fragments = fill_missing_by_reference(fragments, key="title")
        self._log.info("Extracted RCV votes", count=len(fragments))

        return fragments

    def _vote(self, tag: Tag) -> Fragment:
        identifier = self._identifier(tag)
        timestamp = self._timestamp(tag)
        text = self._text(tag)
        (title, rapporteur, reference, description) = parse_rcv_text(
            text,
            # Lists before this date do not contain translated titles
            extract_english=(timestamp.date() >= date(2020, 2, 1)),
        )

        return self._fragment(
            model=Vote,
            source_id=identifier,
            group_key=identifier,
            data={
                "title": title,
                "rapporteur": rapporteur,
                "description": description,
                "reference": reference,
                "timestamp": timestamp,
                "term": self.term,
                "member_votes": self._member_votes(tag),
            },
        )

    def _identifier(self, tag: Tag) -> int:
        # https://github.com/python/typeshed/issues/8755
        attr = cast(str, tag["Identifier"])
        return int(attr)

    def _member_votes(self, tag: Tag) -> list[MemberVote]:
        member_votes: dict[int, MemberVote] = {}

        for member_id in self.active_member_ids:
            member_votes[member_id] = MemberVote(
                web_id=member_id, position=VotePosition.DID_NOT_VOTE
            )

        results = {
            VotePosition.FOR: tag.find("Result.For"),
            VotePosition.AGAINST: tag.find("Result.Against"),
            VotePosition.ABSTENTION: tag.find("Result.Abstention"),
        }

        for position, child in results.items():
            if not isinstance(child, Tag):
                continue

            expected_total = int(cast(str, child["Number"]))
            total = 0

            for member_vote in self._member_votes_by_position(child, position):
                member_votes[member_vote.web_id] = member_vote
                total += 1

            # Sanity check: In addition to the individual members and their vote position,
            # the source RCV lists also contain the total number of members by position. We
            # raise an error if this number doesn’t match the number of extracted members.
            if total != expected_total:
                raise ScrapingError(
                    f"Total number of {total} extracted {position.value} votes "
                    + f"does not match expected {expected_total}"
                )

        return list(member_votes.values())

    def _member_votes_by_position(self, tag: Tag, position: VotePosition) -> list[MemberVote]:
        tags = tag.find_all("PoliticalGroup.Member.Name") + tag.find_all("Member.Name")
        member_votes = []

        for tag in tags:
            member_id = self._member_id_from_tag(tag)
            member_votes.append(MemberVote(web_id=member_id, position=position))

        return member_votes

    def _member_id_from_tag(self, tag: Tag) -> int:
        name = normalize_name(self.ALTERNATE_NAMES.get(tag.text, tag.text))

        id_attribute = tag.get("PersId")
        if isinstance(id_attribute, str):
            # Sanity check to ensure that a record for an active member exists in our
            # database for the referenced ID.
            if int(id_attribute) not in self.member_ids:
                raise ScrapingError(f"Could not find member with ID {id_attribute}")

            return int(id_attribute)

        member_id = self.member_ids_by_last_name.get(name)
        if member_id is not None:
            return member_id

        member_id = self.member_ids_by_full_name.get(name)
        if member_id is not None:
            return member_id

        raise ScrapingError(f"Could not find member ID for name {name}")

    def _timestamp(self, tag: Tag) -> datetime:
        strategies = [
            self._timestamp_from_attribute,
            self._timestamp_from_text,
            self._date_from_attribute,
        ]

        for strategy in strategies:
            try:
                return strategy(tag)
            except ValueError:
                pass

        raise ScrapingError("Could not extract timestamp for vote")

    def _timestamp_from_attribute(self, tag: Tag) -> datetime:
        # https://github.com/python/typeshed/issues/8755
        attr = cast(str, tag["Date"])
        return datetime.strptime(attr, "%Y-%m-%d %H:%M:%S")

    def _timestamp_from_text(self, tag: Tag) -> datetime:
        text_tag = cast(Tag | None, tag.find("RollCallVote.Description.Text"))

        if not text_tag:
            raise ScrapingError("Could not find `RollCallVote.Description.Text` tag.")

        text = text_tag.text.strip()
        match = re.search(self._timestamp_regex(), text)

        if not match:
            raise ScrapingError("Could not extract timestamp from text.")

        return datetime.strptime(match.group(0), "%d/%m/%Y %H:%M:%S.%f")

    def _date_from_attribute(self, tag: Tag) -> datetime:
        # https://github.com/python/typeshed/issues/8755
        attr = cast(str, tag["Date"])
        return datetime.strptime(attr, "%Y-%m-%d")

    def _timestamp_regex(self) -> str:
        # Some older RCV lists contain the full formatted date and time
        # of the vote in the description tag. Newer RCV lists store this
        # information in a separate attribute.
        date = r"{}".format(self.date.strftime("%d/%m/%Y"))
        time = r"\d{2}:\d{2}:\d{2}\.\d{3}"
        return r"" + re.escape(date) + r"\s" + time + r"$"

    def _text(self, tag: Tag) -> str:
        text_tag = cast(Tag | None, tag.find("RollCallVote.Description.Text"))

        if not text_tag:
            raise ScrapingError("Could not find `RollCallVote.Description.Text` tag.")

        text = text_tag.text.strip().removeprefix("- ")

        timestamp_regex = self._timestamp_regex()
        text = re.sub(timestamp_regex, "", text).strip()

        return normalize_whitespace(text)


class RCVListEnglishScraper(BeautifulSoupScraper):
    """Since ~2024 the Parliament has stopped including multilingual (French/English/German)
    titles in the RCV lists. Now, the French version includes only the French title. This
    scraper is used only to extract English titles for votes. We still use the French version
    for all other data, as it is the primary language and often available before other
    translations are published."""

    BS_PARSER = "lxml-xml"
    BASE_URL = "https://www.europarl.europa.eu/doceo/document"

    PROCEDURE_SUFFIXES = [
        "***I",  # Ordinarly Legislative Procedure, 1st reading
        "***II",  # Ordinarly Legislative Procedure, 2nd reading
        "***III",  # Ordinarly Legislative Procedure, 3rd reading
        "***",  # Consent Procedure
        "*",  # Consultation Procedure
    ]

    def __init__(self, date: date, term: int, request_cache: RequestCache | None = None):
        super().__init__(date=date, term=term, request_cache=request_cache)
        self.date = date
        self.term = term

    def _url(self) -> str:
        date = self.date.strftime("%Y-%m-%d")
        url = f"{self.BASE_URL}/PV-{self.term}-{date}-RCV_EN.xml"

        return url

    def _extract_data(self, doc: BeautifulSoup) -> Iterator[Fragment]:
        title_by_dlv_id: dict[int, str] = {}

        for tag in doc.find_all("VoteTitle"):
            dlv_id = int(tag["DlvId"])
            title = tag.text.strip()
            title_by_dlv_id[dlv_id] = title

        for tag in doc.find_all("RollCallVote.Result"):
            doceo_vote_id = int(tag["Identifier"])
            dlv_id = int(tag["DlvId"])
            title = title_by_dlv_id[dlv_id]

            for suffix in self.PROCEDURE_SUFFIXES:
                title = title.removesuffix(suffix).strip()

            yield self._fragment(
                model=Vote,
                source_id=doceo_vote_id,
                group_key=doceo_vote_id,
                data={"dlv_title": title},
            )


class DocumentScraper(BeautifulSoupScraper):
    BS_PARSER = "lxml"
    BASE_URL = "https://www.europarl.europa.eu/doceo/document"
    PROCEDURE_URL_REGEX = re.compile(
        r"^https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do"
    )

    def __init__(
        self,
        vote_id: int,
        reference: str,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(vote_id=vote_id, reference=reference, request_cache=request_cache)
        self.vote_id = vote_id
        self.reference = reference

    def _url(self) -> str:
        ref = parse_reference(self.reference)
        number = str(ref["number"]).rjust(4, "0")
        formatted_ref = f"{ref['type']}-{ref['term']}-{ref['year']}-{number}"
        return f"{self.BASE_URL}/{formatted_ref}_EN.html"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment:
        procedure_reference = self._procedure_reference(doc)

        self._log.info(
            "Extracted document information",
            procedure_reference=procedure_reference,
        )

        return self._fragment(
            model=Vote,
            source_id=self.vote_id,
            group_key=self.vote_id,
            data={"procedure_reference": procedure_reference},
        )

    def _procedure_reference(self, doc: BeautifulSoup) -> str | None:
        container = doc.select_one(".doceo-ring")

        if not container:
            return None

        procedure_link = container.find("a", href=self.PROCEDURE_URL_REGEX)

        if not procedure_link:
            return None

        return procedure_link.get_text(strip=True)


class ProcedureScraper(BeautifulSoupScraper):
    BS_PARSER = "lxml"
    BASE_URL = "https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference="

    TITLE_PREFIXES = ["Resolution on", "Motion"]

    def __init__(
        self,
        vote_id: int,
        procedure_reference: str,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(
            vote_id=vote_id,
            procedure_reference=procedure_reference,
            request_cache=request_cache,
        )
        self.vote_id = vote_id
        self.procedure_reference = procedure_reference

    def _url(self) -> str:
        return f"{self.BASE_URL}{self.procedure_reference}"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment:
        title = self._title(doc)
        geo_areas = self._geo_areas(doc)
        responsible_committee = self._responsible_committee(doc)
        self._log.info(
            "Extracted procedure information",
            title=title,
            geo_areas=geo_areas,
        )

        return self._fragment(
            model=Vote,
            source_id=self.vote_id,
            group_key=self.vote_id,
            data={
                "procedure_title": title,
                "geo_areas": geo_areas,
                "responsible_committee": responsible_committee,
            },
        )

    def _title(self, doc: BeautifulSoup) -> str | None:
        title = doc.select_one("#website-body h2.erpl_title-h2")

        if not title:
            return None

        normalized_title = title.text

        for prefix in self.TITLE_PREFIXES:
            normalized_title = normalized_title.removeprefix(prefix).strip()

        return normalized_title[:1].upper() + normalized_title[1:]

    def _geo_areas(self, doc: BeautifulSoup) -> list[str]:
        # The website unfortunately doesn't use semantic markup, so we have
        # to rely on visual properties
        wrapper = doc.select_one(
            '#section1 p.font-weight-bold:-soup-contains("Geographical area") + p'
        )

        if not wrapper:
            return []

        geo_areas = []

        for node in wrapper.children:
            country_name = node.get_text(strip=True)

            if not country_name:
                continue

            country = Country.from_label(country_name, fuzzy=True)

            if not country:
                log.warning("Geographical area not found", name=country_name)
                continue

            geo_areas.append(country.code)

        return geo_areas

    def _responsible_committee(self, doc: BeautifulSoup) -> str | None:
        table = doc.select_one(
            '#erpl_accordion-committee table:has(th:-soup-contains("Committee responsible"))'
        )

        if not table:
            return None

        if len(table.select("tbody tr")) > 1:
            # We assume that there is at most one responsible committee
            log.warning("More than one responsible committee found")

        badge = table.select_one("tbody tr .erpl_badge-committee")

        if not badge:
            return None

        text = badge.text.strip()
        committee = Committee.get(text)

        if not committee:
            raise ScrapingError(f"Could not find committee {text}")

        return committee.code


class EurlexProcedureScraper(BeautifulSoupScraper):
    """Scrapes EuroVoc concepts from the procedure page on EUR-Lex. EuroVoc is thesaurus
    maintained by the EU Publications Office. Most interinstitutional procedures are assigned
    multiple EuroVoc concepts (i.e. tags) that we can use to improve search recall or to
    fetch related votes. In theory, it should also be possible to fetch these via a SPARQL
    endpoint. However, I wasn’t able to come up with a query that reliably returned EuroVoc
    concepts that were consitent with what’s displayed on EUR-Lex."""

    BS_PARSER = "lxml"
    BASE_URL = "https://eur-lex.europa.eu/procedure/EN"
    EUROVOC_URL_REGEX = re.compile(r"LP_DC_CODED=")

    def __init__(
        self,
        vote_id: int,
        procedure_reference: str,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(
            vote_id=vote_id,
            procedure_reference=procedure_reference,
            request_cache=request_cache,
        )
        self.vote_id = vote_id
        self.procedure_reference = procedure_reference

    def _url(self) -> str:
        ref = parse_procedure_reference(self.procedure_reference)

        # EUR-Lex URLs have the format `https://eur-lex.europa.eu/procedure/2021_160` whereas
        # the procedure reference is usually formatted with leading zeros: `2021/0160(COD)`.
        number = ref["number"].lstrip("0")

        return f"{self.BASE_URL}/{ref['year']}_{number}"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment | None:
        container = doc.select_one("#eurovocProc")

        if not container:
            return None

        eurovoc_concepts: set[str] = set()
        geo_areas: set[str] = set()
        links = container.find_all("a", href=self.EUROVOC_URL_REGEX)

        for link in links:
            url = urlparse(link["href"])
            query = parse_qs(url.query)
            eurovoc_id = query.get("LP_DC_CODED")

            if not eurovoc_id:
                continue

            eurovoc_concept = EurovocConcept.get(eurovoc_id[0])

            if not eurovoc_concept:
                continue

            if eurovoc_concept.geo_area:
                geo_areas.add(eurovoc_concept.geo_area.code)
            else:
                eurovoc_concepts.add(eurovoc_concept.id)

        self._log.info(
            "Extracted EurLex procedure information",
            eurovoc_terms=eurovoc_concepts,
            geo_areas=geo_areas,
        )

        return self._fragment(
            model=Vote,
            source_id=self.vote_id,
            group_key=self.vote_id,
            data={
                "eurovoc_concepts": eurovoc_concepts,
                "geo_areas": geo_areas,
            },
        )


class EurlexDocumentScraper(BeautifulSoupScraper):
    """Scrapes EuroVoc concepts from the document page on EUR-Lex. This scraper is very
    similar to and complements the `EurlexDocumentScraper`. In some cases, the procedure
    page on EUR-Lex doesn’t include any EuroVoc concepts, but the document page does."""

    BS_PARSER = "lxml"
    BASE_URL = "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=EP:"
    EUROVOC_URL_REGEX = re.compile(r"DC_CODED=")

    def __init__(
        self,
        vote_id: int,
        reference: str,
        request_cache: RequestCache | None = None,
    ):
        super().__init__(vote_id=vote_id, reference=reference, request_cache=request_cache)
        self.vote_id = vote_id
        self.reference = reference

    def _url(self) -> str:
        ref = parse_reference(self.reference)
        number = str(ref["number"]).rjust(4, "0")

        # EUR-Lex URLs have the format `https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=EP:P9_A(2021)0270`
        # whereas the reference is usually formatted like this: `A9-0270/2021`.
        return f"{self.BASE_URL}P{ref['term']}_{ref['type']}({ref['year']}){number}"

    def _extract_data(self, doc: BeautifulSoup) -> Fragment | None:
        container = doc.select_one("#PPClass_Contents")

        if not container:
            return None

        eurovoc_concepts: set[str] = set()
        geo_areas: set[str] = set()
        links = container.find_all("a", href=self.EUROVOC_URL_REGEX)

        for link in links:
            url = urlparse(link["href"])
            query = parse_qs(url.query)
            eurovoc_id = query.get("DC_CODED")

            if not eurovoc_id:
                continue

            eurovoc_concept = EurovocConcept.get(eurovoc_id[0])

            if not eurovoc_concept:
                continue

            if eurovoc_concept.geo_area:
                geo_areas.add(eurovoc_concept.geo_area.code)
            else:
                eurovoc_concepts.add(eurovoc_concept.id)

        self._log.info(
            "Extracted EurLex document information",
            eurovoc_terms=eurovoc_concepts,
            geo_areas=geo_areas,
        )

        return self._fragment(
            model=Vote,
            source_id=self.vote_id,
            group_key=self.vote_id,
            data={
                "eurovoc_concepts": eurovoc_concepts,
                "geo_areas": geo_areas,
            },
        )
