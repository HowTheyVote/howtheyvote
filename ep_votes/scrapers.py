from xml.etree import ElementTree
from bs4 import BeautifulSoup
import requests
from io import StringIO
from datetime import date
from .types import Member, Country


class MembersXMLScraper:
    TERMS = [8, 9]
    DIRECTORY_BASE_URL = "https://www.europarl.europa.eu/meps/en/directory/xml"

    def __init__(self):
        self._members = {}

    def run(self):
        self._download()

        for term in self.TERMS:
            for member in self._get_members(term):
                self._add_member(member)

        return list(self._members.values())

    def _add_member(self, member):
        web_id = member.europarl_website_id

        if web_id not in self._members:
            self._members[web_id] = member
            return

        self._members[web_id].terms = self._members[web_id].terms | member.terms

    def _download(self):
        self._terms = {}

        for term in self.TERMS:
            raw = self._download_term(term)
            self._terms[term] = ElementTree.parse(raw)

    def _download_term(self, term):
        xml = requests.get(self._term_url(term)).text
        return StringIO(xml)

    def _term_url(self, term):
        return f"{self.DIRECTORY_BASE_URL}/?leg={term}"

    def _get_members(self, term):
        tags = self._terms[term].findall("mep")
        return [self._get_member(tag, term) for tag in tags]

    def _get_member(self, tag: ElementTree, term):
        europarl_website_id = int(tag.find("id").text)

        return Member(europarl_website_id=europarl_website_id, terms={term})


class MemberInfoHTMLScraper:
    PROFILE_BASE_URL = "https://europarl.europa.eu/meps/en"

    def __init__(self, member: Member):
        self._member = member

    def run(self):
        self._download()

        first_name, last_name = Member.parse_full_name(self._full_name())

        member = Member(
            europarl_website_id=self._member.europarl_website_id,
            terms=set(self._member.terms),
            first_name=first_name,
            last_name=last_name,
            date_of_birth=self._date_of_birth(),
            country=self._country(),
        )

        return member

    def _download(self):
        self._terms = {}

        for term in self._member.terms:
            raw = self._download_term(term)
            self._terms[term] = BeautifulSoup(raw, "lxml")

    def _download_term(self, term):
        return requests.get(self._profile_url(term)).text

    def _profile_url(self, term):
        web_id = self._member.europarl_website_id
        return f"{self.PROFILE_BASE_URL}/{web_id}/NAME/history/{term}"

    def _latest_term(self):
        return self._terms[max(self._member.terms)]

    def _full_name(self):
        html = self._latest_term()
        return html.select("#presentationmep div.erpl_title-h1")[0].text.strip()

    def _date_of_birth(self):
        raw = self._latest_term().select("#birthDate")[0].text.strip()

        year = int(raw[6:])
        month = int(raw[3:5])
        day = int(raw[:2])

        return date(year, month, day)

    def _country(self):
        html = self._latest_term()
        raw = html.select("#presentationmep div.erpl_title-h3")[0].text
        country = raw.split("-")[0].strip()

        return Country.from_str(country)
