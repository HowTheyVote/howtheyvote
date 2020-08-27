from xml.etree import ElementTree
import requests
from io import StringIO
from .types import Member, Group, Country


class MembersXMLScraper:
    CURRENT_MEMBERS_URL = "https://europarl.europa.eu/meps/en/full-list/xml"

    def run(self):
        self._xml = self._download_xml()
        self._parsed = self._parse_xml()

        return self._get_members()

    def _download_xml(self):
        xml = requests.get(self.CURRENT_MEMBERS_URL).text
        return StringIO(xml)

    def _parse_xml(self):
        return ElementTree.parse(self._xml)

    def _get_members(self):
        member_tags = self._parsed.findall("mep")
        return [self._get_member(tag) for tag in member_tags]

    def _get_member(self, subtree: ElementTree):
        full_name = subtree.find("fullName").text
        first_name, last_name = Member.parse_full_name(full_name)
        country = Country.from_str(subtree.find("country").text)
        group = Group.from_str(subtree.find("politicalGroup").text)
        europarl_website_id = int(subtree.find("id").text)

        return Member(
            first_name=first_name,
            last_name=last_name,
            country=country,
            group=group,
            europarl_website_id=europarl_website_id,
        )
