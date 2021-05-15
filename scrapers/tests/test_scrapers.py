import pytest
from requests_mock import ANY
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup
from ep_votes.scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    VotingListsScraper,
    VoteCollectionsScraper,
)
from ep_votes.models import (
    Member,
    MemberInfo,
    Country,
    Group,
    GroupMembership,
    Position,
    Voting,
    VotingList,
    VoteResult,
    VoteType,
    Vote,
)

TEST_DATA_DIR = Path(__file__).resolve().parent / "data"


def mock_response(req, context):
    url = req.url
    url = url.replace("https://www.europarl.europa.eu", "")

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
        "/doceo/document/PV-9-2021-03-09-RCV_FR.xml": "pv-9-2021-09-03-rcv-fr.xml",
        "/doceo/document/PV-9-2021-03-09-VOT_EN.xml": "pv-9-2021-09-03-vot-en.xml",
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


def test_voting_lists_scraper_run(mock_request):
    scraper = VotingListsScraper(term=9, date=date(2020, 7, 23))

    votings = [
        Voting(doceo_member_id=7244, name="Aguilar", position=Position.FOR),
        Voting(doceo_member_id=6630, name="de Graaff", position=Position.AGAINST),
        Voting(doceo_member_id=6836, name="Kolakušić", position=Position.ABSTENTION),
    ]

    expected = [
        VotingList(
            description="B9-0229/2020 - § 1/1",
            reference="B9-0229/2020",
            doceo_vote_id=116365,
            votings=votings,
        )
    ]

    assert scraper.run() == expected


def test_voting_lists_scraper_run_positions_missing(mock_request):
    scraper = VotingListsScraper(term=9, date=date(2019, 10, 22))

    votings = [
        Voting(doceo_member_id=5602, name="Ždanoka", position=Position.FOR),
        Voting(doceo_member_id=6752, name="Mobarik", position=Position.ABSTENTION),
    ]

    voting_lists = scraper.run()

    assert voting_lists[0].votings == votings


def test_vote_collections_scraper_url():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))

    expected = "https://europarl.europa.eu/doceo/document/PV-9-2021-03-09-VOT_EN.xml"
    assert scraper._url() == expected


def test_vote_collections_scraper_run():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))
    result = scraper.run()
    assert len(result) == 22

    assert result[0].title == "InvestEU programme ***I"
    assert result[0].reference == "A9-0203/2020"

    assert result[21].title == "Children’s rights"
    assert (
        result[12].title
        == "Objection pursuant to Rule 112(2) and (3): Genetically modified maize MZIR098 (SYN-ØØØ98-3)"
    )
    assert result[21].reference == "B9-0164/2021"


def test_vote_collections_scraper_run_vote_items():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))
    result = scraper.run()

    assert len(result[3].votes) == 8

    expected_votes = [
        Vote(
            subject="Amendments by the committee responsible – put to the vote collectively",
            subheading=None,
            author="committee",
            result=VoteResult.ADOPTED,
            split_part=None,
            amendment="1-65, 67-76",
            type=VoteType.AMENDMENT,
            remarks="5624094",
        ),
        Vote(
            subject="§ 5, sub§ 1",
            subheading=None,
            author="committee",
            result=VoteResult.ADOPTED,
            split_part=None,
            amendment="66",
            type=VoteType.AMENDMENT,
            remarks="53614713",
        ),
        Vote(
            subject="After recital 2",
            subheading=None,
            author="ID",
            result=VoteResult.REJECTED,
            split_part=None,
            amendment="77",
            type=VoteType.AMENDMENT,
            remarks="8758423",
        ),
        Vote(
            subject="Recital 3",
            subheading=None,
            author="ID",
            result=VoteResult.REJECTED,
            split_part=None,
            amendment="78",
            type=VoteType.AMENDMENT,
            remarks="5858650",
        ),
        Vote(
            subject="Recital 8",
            subheading=None,
            author="ID",
            result=VoteResult.REJECTED,
            split_part=None,
            amendment="79",
            type=VoteType.AMENDMENT,
            remarks="9757819",
        ),
        Vote(
            subject="Recital 15",
            subheading=None,
            author="ID",
            result=VoteResult.REJECTED,
            split_part=None,
            amendment="80",
            type=VoteType.AMENDMENT,
            remarks="9458911",
        ),
        Vote(
            subject="Recital 25",
            subheading=None,
            author="ID",
            result=VoteResult.REJECTED,
            split_part=None,
            amendment="81",
            type=VoteType.AMENDMENT,
            remarks="8759115",
        ),
        Vote(
            subject="Commission proposal",
            subheading=None,
            author=None,
            result=VoteResult.ADOPTED,
            split_part=None,
            amendment=None,
            type=VoteType.PRIMARY,
            remarks="5686364",
        ),
    ]

    assert result[3].votes == expected_votes

    expected_votes = [
        Vote(
            subject="§ 1",
            subheading="Amendments to the paragraphs of the motion for a resolution",
            author="original text",
            result=VoteResult.ADOPTED,
            split_part=1,
            amendment=None,
            type=VoteType.SEPARATE,
            remarks="6612015",
        ),
        Vote(
            subject="§ 1",
            subheading="Amendments to the paragraphs of the motion for a resolution",
            author="original text",
            result=VoteResult.ADOPTED,
            split_part=2,
            amendment=None,
            type=VoteType.SEPARATE,
            remarks="5401488",
        ),
        Vote(
            subject="§ 1",
            subheading="Amendments to the paragraphs of the motion for a resolution",
            author="original text",
            result=VoteResult.ADOPTED,
            split_part=3,
            amendment=None,
            type=VoteType.SEPARATE,
            remarks="53215212",
        ),
    ]

    assert result[4].votes[:3] == expected_votes


def test_vote_collections_scraper_add_subheading():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))

    table = [
        {"Subject": "A very important topic"},
        {
            "Subject": "Proposal",
            "RCV etc.": "RCV",
            "Vote": "+",
            "RCV/EV – remarks": "100, 50, 25",
        },
    ]

    expected_table = [
        {"Subject": "A very important topic"},
        {
            "Subject": "Proposal",
            "RCV etc.": "RCV",
            "Vote": "+",
            "RCV/EV – remarks": "100, 50, 25",
            "Subheading": "A very important topic",
        },
    ]

    assert scraper._add_subheading(table) == expected_table


def test_vote_collections_scraper_include_row_heading():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))

    rows = [
        {"c1": "Amendments to the recitals"},
        {
            "Subject": "After recital G",
            "Am No": "1",
            "Author": "ECR",
            "RCV etc.": "RCV",
            "Vote": "-",
            "RCV/EV – remarks": "134, 539, 22",
        },
    ]

    assert scraper._include_row(rows[0]) is False
    assert scraper._include_row(rows[1]) is True


def test_vote_collections_scraper_include_row_lapsed():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))

    rows = [
        {
            "Subject": "After recital G",
            "Am No": "1",
            "Author": "ECR",
            "RCV etc.": "RCV",
            "Vote": "↓",
            "RCV/EV – remarks": "134, 539, 22",
        },
        {
            "Subject": "After recital G",
            "Am No": "1",
            "Author": "ECR",
            "RCV etc.": "RCV",
            "Vote": "+",
            "RCV/EV – remarks": "134, 539, 22",
        },
        {
            "Subject": "After recital G",
            "Am No": "1",
            "Author": "ECR",
            "RCV etc.": "RCV",
            "Vote": "-",
            "RCV/EV – remarks": "134, 539, 22",
        },
    ]

    assert scraper._include_row(rows[0]) is False
    assert scraper._include_row(rows[1]) is True
    assert scraper._include_row(rows[2]) is True


def test_vote_collections_scraper_include_row_no_rcv():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))

    rows = [
        {"c1": "Proposal for a decision", "c2": "SEC", "c3": "+", "c4": "400, 248, 45"},
        {
            "Subject": "§5",
            "Am No": "§",
            "Author": "original text",
            "RCV etc.": "split",
            "Vote": "",
            "RCV/EV – remarks": "",
        },
        {
            "Subject": "§5",
            "Am No": "§",
            "Author": "original text",
            "RCV etc.": "1/RCV",
            "Vote": "+",
            "RCV/EV – remarks": "585, 69, 42",
        },
        {
            "Subject": "Recital 17",
            "Am No": "25",
            "Author": "MEPs",
            "RCV etc.": "RCV",
            "Vote": "-",
            "RCV/EV – remarks": "181, 481, 33",
        },
    ]

    assert scraper._include_row(rows[0]) is False
    assert scraper._include_row(rows[1]) is False

    assert scraper._include_row(rows[2]) is True
    assert scraper._include_row(rows[3]) is True
