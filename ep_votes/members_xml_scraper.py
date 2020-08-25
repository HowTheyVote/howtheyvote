from xml.etree import ElementTree
from .member import Member, parse_name
from .group import Group
from .country import Country


class MembersXMLScraper:
    # TODO Set import in `__init__` and parse
    # XML during construction

    def __init__(self):
        self._input = None
        self._parsed = None

    def _parse_input(self):
        self._parsed = ElementTree.parse(self._input)

    def get_members(self):
        member_tags = self._parsed.findall("mep")

        return [self._get_member(tag) for tag in member_tags]

    def _get_member(self, subtree: ElementTree):
        full_name = subtree.find("fullName").text
        first_name, last_name = parse_name(full_name)
        country = Country.from_str(subtree.find("country").text)
        group = Group.from_str(subtree.find("politicalGroup").text)
        term = None
        europarl_website_id = int(subtree.find("id").text)

        return Member(
            first_name=first_name,
            last_name=last_name,
            country=country,
            group=group,
            term=term,
            europarl_website_id=europarl_website_id,
        )
