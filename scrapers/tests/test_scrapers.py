import pytest
from requests_mock import ANY
from pathlib import Path
from datetime import date, datetime
from bs4 import BeautifulSoup
from ep_votes.scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VoteResultsScraper,
    DocumentInfoScraper,
    ProcedureScraper,
)
from ep_votes.models import (
    Member,
    MemberInfo,
    Country,
    Group,
    GroupMembership,
    Position,
    Voting,
    VoteType,
    Vote,
    Doc,
    DocReference,
    DocType,
    Procedure,
    ProcedureReference,
    ProcedureType,
)

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


def mock_response(req, context):
    url = req.url
    url = url.replace("https://europarl.europa.eu", "")
    url = url.replace("https://oeil.secure.europarl.europa.eu", "")

    MOCK_RESPONSES = {
        "/meps/en/directory/xml/?leg=8": "directory_term_8.xml",
        "/meps/en/directory/xml/?leg=9": "directory_term_9.xml",
        "/meps/en/124834/NAME/home": "sonneborn_home.html",
        "/meps/en/124834/NAME/history/8": "sonneborn_term_8.html",
        "/meps/en/124834/NAME/history/9": "sonneborn_term_9.html",
        "/meps/en/124831/NAME/home": "adinolfi_home.html",
        "/meps/en/124831/NAME/history/8": "adinolfi_term_8.html",
        "/meps/en/124831/NAME/history/9": "adinolfi_term_9.html",
        "/doceo/document/PV-9-2020-07-23-RCV_FR.xml": "pv-9-2020-07-23-rcv-fr.xml",
        "/doceo/document/PV-9-2019-10-22-RCV_FR.xml": "pv-9-2019-10-22-rcv-fr.xml",
        "/doceo/document/B-9-2020-0220_EN.html": "b-9-2020-0220-en.html",
        "/oeil/popups/printresultlist.xml?lang=en&limit=1&q=documentEP:D-B9-0154/2019": "procedure-b9-0154-2019.xml",
    }

    file = MOCK_RESPONSES[url]
    path = TEST_DATA_DIR / file

    return Path(path).read_text()


@pytest.fixture
def mock_request(requests_mock):
    requests_mock.get(ANY, text=mock_response)
    yield requests_mock


def test_members_scraper_run(mock_request):
    scraper = MembersScraper(term=9)

    expected = [
        Member(terms=[9], web_id=1),
        Member(terms=[9], web_id=2),
    ]

    assert scraper.run() == expected


def test_member_info_scraper_run(mock_request):
    scraper = MemberInfoScraper(web_id=124834)

    expected = MemberInfo(
        first_name="Martin",
        last_name="SONNEBORN",
        date_of_birth=date(1965, 5, 15),
        country=Country.DE,
    )

    assert scraper.run() == expected


def test_member_info_scraper_date_of_birth_without(mock_request):
    scraper = MemberInfoScraper(web_id=124831)
    scraper._load()
    assert scraper._date_of_birth() is None


def test_member_groups_scraper_run(mock_request):
    scraper = MemberGroupsScraper(web_id=124834, term=8)

    expected = [
        GroupMembership(
            group=Group.NI,
            term=8,
            start_date=date(2014, 7, 1),
            end_date=date(2019, 7, 1),
        ),
    ]

    assert scraper.run() == expected


def test_member_groups_scraper_date_range(mock_request):
    scraper = MemberGroupsScraper(web_id=123, term=8)

    tags = [
        "<strong>01-07-2014 / 01-07-2019</strong> : Group XYZ",
        "<strong>02-07-2019 ...</strong> : Group XYZ",
    ]

    tags = [BeautifulSoup(tag, "lxml").body for tag in tags]

    assert scraper._date_range(tags[0]) == (date(2014, 7, 1), date(2019, 7, 1))
    assert scraper._date_range(tags[1]) == (date(2019, 7, 2), None)


def test_member_groups_scraper_group(mock_request):
    scraper = MemberGroupsScraper(web_id=123, term=8)

    tags = [
        "<strong>02-07-2019 ...</strong> : Renew Europe Group - Member",
        "<strong>02-07-2019 ...</strong> : Group of the European People's Party (Christian Democrats) - Chair",
        "<strong>02-07-2019 ...</strong> : Group of the European United Left - Nordic Green Left - Co-Chair",
        "<strong>02-07-2019 ...</strong> : Group of the Greens/European Free Alliance - Vice-Chair",
        "<strong>14-05-2020 ...</strong> : European Conservatives and Reformists Group - Member of the Bureau",
        "<strong>02-07-2019 ...</strong> : Group of the Progressive Alliance of Socialists and Democrats in the European Parliament - First Vice-Chair",
        "<strong>02-07-2019 ...</strong> : European Conservatives and Reformists Group - Co-treasurer",
        "<strong>02-07-2019 ...</strong> : Non-attached Members",
    ]

    tags = [BeautifulSoup(tag, "lxml").body for tag in tags]

    assert scraper._group(tags[0]) == Group.RENEW
    assert scraper._group(tags[1]) == Group.EPP
    assert scraper._group(tags[2]) == Group.GUE
    assert scraper._group(tags[3]) == Group.GREENS
    assert scraper._group(tags[4]) == Group.ECR
    assert scraper._group(tags[5]) == Group.SD
    assert scraper._group(tags[6]) == Group.ECR
    assert scraper._group(tags[7]) == Group.NI


def test_vote_results_scraper_run(mock_request):
    scraper = VoteResultsScraper(term=9, date=date(2020, 7, 23))

    votings = [
        Voting(doceo_member_id=7244, name="Aguilar", position=Position.FOR),
        Voting(doceo_member_id=6630, name="de Graaff", position=Position.AGAINST),
        Voting(doceo_member_id=6836, name="Kolakušić", position=Position.ABSTENTION),
    ]

    votes = [
        Vote(
            doceo_vote_id=116365,
            date=datetime(2020, 7, 23, 12, 49, 32),
            description="§ 1/1",
            reference=DocReference(type=DocType.B, term=9, number=229, year=2020),
            votings=votings,
            vote_type=VoteType.SPLIT,
        )
    ]

    assert scraper.run() == votes


def test_vote_results_scraper_run_positions_missing(mock_request):
    scraper = VoteResultsScraper(term=9, date=date(2019, 10, 22))

    votings = [
        Voting(doceo_member_id=5602, name="Ždanoka", position=Position.FOR),
        Voting(doceo_member_id=6752, name="Mobarik", position=Position.ABSTENTION),
    ]

    votes = scraper.run()

    assert votes[0].votings == votings


@pytest.fixture
def tags_for_description():
    descriptions = [
        (  # Handles resolution references (iPlRe)
            "<RollCallVote.Description.Text>"
            '<a redmap-uri="/reds:iPlRe/B-9-2019-0029">B9-0229/2020</a> - § 1/1'
            "</RollCallVote.Description.Text>"
        ),
        (
            # Handles report references (iPlRp)
            "<RollCallVote.Description.Text>"
            '<a redmap-uri="/reds:iPlRp/A-9-2019-0017">A9-0017/2019</a> - '
            "Monika Hohlmeier et Eider Gardiazabal Rubial - Am 49"
            "</RollCallVote.Description.Text>"
        ),
        (  # Handles descriptions without document references
            "<RollCallVote.Description.Text>"
            "Ordre du jour de mardi - demande du groupe GUE/NGL"
            "</RollCallVote.Description.Text>"
        ),
        (  # Ignore references to non-plenary documents
            "<RollCallVote.Description.Text>"
            "Proposition de règlement "
            "("
            '<a redmap-uri="/reds:iEcCom/COM-2019-0396">COM(2019)0396</a>'
            "- C9-0108/2019-"
            '<a redmap-uri="/reds:DirContProc/COD-2019-0179">2019/0179(COD)</a>'
            ")"
            "</RollCallVote.Description.Text>"
        ),
        (  # Removes additional whitespace
            "<RollCallVote.Description.Text>"
            '<a redmap-uri="/reds:iPlRp/A-9-2019-0020">A9-0020/2019</a>'
            "-    Younous Omarjee - Vote unique"
            "</RollCallVote.Description.Text>"
        ),
    ]

    return [BeautifulSoup(desc, "lxml-xml") for desc in descriptions]


def test_vote_results_scraper_description(tags_for_description):
    scraper = VoteResultsScraper(term=9, date=date(2020, 7, 23))

    expected = [
        "§ 1/1",
        "Monika Hohlmeier et Eider Gardiazabal Rubial - Am 49",
        "Ordre du jour de mardi - demande du groupe GUE/NGL",
        "Proposition de règlement (COM(2019)0396- C9-0108/2019-2019/0179(COD))",
        "Younous Omarjee - Vote unique",
    ]

    assert scraper._description(tags_for_description[0]) == expected[0]
    assert scraper._description(tags_for_description[1]) == expected[1]
    assert scraper._description(tags_for_description[2]) == expected[2]


def test_vote_results_scraper_reference(tags_for_description):
    scraper = VoteResultsScraper(term=9, date=date(2020, 7, 23))

    expected = [
        DocReference.from_str("B9-0229/2020"),
        DocReference.from_str("A9-0017/2019"),
        None,
        None,
        DocReference.from_str("A9-0020/2019"),
    ]

    assert scraper._reference(tags_for_description[0]) == expected[0]
    assert scraper._reference(tags_for_description[1]) == expected[1]
    assert scraper._reference(tags_for_description[2]) == expected[2]


@pytest.fixture
def tags_for_type():
    descriptions = [
        "<RollCallVote.Description.Text>Text</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Am 1</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Am 11</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Am 1/2</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Am  1/2</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - §1</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - §11</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - §1/2</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - § 1</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Considérant A</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Considerant A</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Considerant AB</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Considerant A/1</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Am 1 Am 2</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Am 1 - 5</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - Am 1 Am 3 - 5</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - §1 §2</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - §1 - 5</RollCallVote.Description.Text>",
        "<RollCallVote.Description.Text>Text - §1 §3 - 5</RollCallVote.Description.Text>",
    ]

    return [BeautifulSoup(desc, "lxml-xml") for desc in descriptions]


def test_vote_results_scraper_type(tags_for_type):
    scraper = VoteResultsScraper(term=9, date=date(2020, 7, 23))

    # by default, if no special vote identifier is found, it's a final vote
    assert scraper._type(tags_for_type[0]) == VoteType.FINAL

    # amendments
    assert scraper._type(tags_for_type[1]) == VoteType.AMENDMENT
    assert scraper._type(tags_for_type[2]) == VoteType.AMENDMENT
    assert scraper._type(tags_for_type[3]) == VoteType.AMENDMENT
    assert scraper._type(tags_for_type[4]) == VoteType.AMENDMENT

    # paragraphs
    assert scraper._type(tags_for_type[5]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[6]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[7]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[8]) == VoteType.SPLIT

    # considerant
    assert scraper._type(tags_for_type[9]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[10]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[11]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[12]) == VoteType.SPLIT

    # multiple amendments
    assert scraper._type(tags_for_type[13]) == VoteType.AMENDMENT
    assert scraper._type(tags_for_type[14]) == VoteType.AMENDMENT
    assert scraper._type(tags_for_type[15]) == VoteType.AMENDMENT

    # multiple paragraphs
    assert scraper._type(tags_for_type[16]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[17]) == VoteType.SPLIT
    assert scraper._type(tags_for_type[18]) == VoteType.SPLIT


def test_document_scraper_run(mock_request):
    title = "MOTION FOR A RESOLUTION on the EU’s public health strategy post-COVID-19"

    scraper = DocumentInfoScraper(
        type=DocType.B,
        term=9,
        number=220,
        year=2020,
    )

    expected = Doc(title=title)

    assert scraper.run() == expected


def test_procedure_scraper_run(mock_request):
    title = "Search and rescue in the Mediterranean (SAR)"

    scraper = ProcedureScraper(
        type=DocType.B,
        term=9,
        year=2019,
        number=154,
    )

    expected_reference = ProcedureReference(
        type=ProcedureType.RSP,
        year=2019,
        number=2755,
    )

    expected = Procedure(
        title=title,
        reference=expected_reference,
    )

    assert scraper.run() == expected


@pytest.fixture
def procedure_title_tags():
    descriptions = [
        (  # Handles leading/trailing white space
            "<title>"
            "<![CDATA[ Search and rescue in the Mediterranean (SAR) ]]>"
            "</title>"
        ),
        (
            # Handles line breaks
            "<title>"
            "<![CDATA[ Decision to raise no objections to the draft Commission\n"
            "regulation amending Regulation (EC) No 1126/2008 adopting certain\n"
            "international accounting standards in accordance with Regulation\n"
            "(EC) No 1606/2002 of the European Parliament and of the Council as\n"
            "regards International Accounting Standard 39, International\n"
            "Financial Reporting Standards 7 and 9 ]]>"
            "</title>"
        ),
    ]

    return [BeautifulSoup(desc, "lxml-xml") for desc in descriptions]


def test_procedure_scraper_title(procedure_title_tags):
    scraper = ProcedureScraper(
        type=DocType.B,
        term=9,
        year=2019,
        number=154,
    )

    expected = [
        "Search and rescue in the Mediterranean (SAR)",
        (
            "Decision to raise no objections to the draft Commission "
            "regulation amending Regulation (EC) No 1126/2008 adopting certain "
            "international accounting standards in accordance with Regulation "
            "(EC) No 1606/2002 of the European Parliament and of the Council as "
            "regards International Accounting Standard 39, International "
            "Financial Reporting Standards 7 and 9"
        ),
    ]

    assert scraper._title(procedure_title_tags[0]) == expected[0]
    assert scraper._title(procedure_title_tags[1]) == expected[1]
