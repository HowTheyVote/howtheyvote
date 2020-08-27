from xml.etree import ElementTree
import requests
from io import StringIO
from .types import Member


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
        full_name = tag.find("fullName").text
        first_name, last_name = Member.parse_full_name(full_name)
        europarl_website_id = int(tag.find("id").text)

        return Member(
            first_name=first_name,
            last_name=last_name,
            europarl_website_id=europarl_website_id,
            terms={term},
        )
