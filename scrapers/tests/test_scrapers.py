import pytest
from requests_mock import ANY
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup
from ep_votes.scrapers import (
    MembersScraper,
    MemberInfoScraper,
    MemberGroupsScraper,
    SessionsScraper,
    VotingListsScraper,
    VoteCollectionsScraper,
    SummaryIDScraper,
    SummaryScraper,
    ScrapingException,
)
from ep_votes.models import (
    Location,
    Member,
    MemberInfo,
    Country,
    Group,
    GroupMembership,
    Position,
    Session,
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
        "/doceo/document/PV-9-2021-03-09-RCV_FR.xml": "pv-9-2021-09-03-rcv-fr.xml",
        "/RegData/seance_pleniere/proces_verbal/2019/03-26/liste_presence/P8_PV(2019)03-26(RCV)_XC.xml": "p8_pv(2019)03-26(rcv)_xc.xml",
        "/doceo/document/PV-9-2021-03-09-VOT_EN.xml": "pv-9-2021-09-03-vot-en.xml",
        "/RegData/seance_pleniere/proces_verbal/2019/03-26/liste_presence/P8_PV(2019)03-26(VOT)_EN.xml": "p8_pv(2019)03-26(vot)_en.xml",
        "/oeil/popups/ficheprocedure.do?reference=B9-0116/2021": "ficheprocedure_b9-0116-2021.html",
        "/oeil/popups/ficheprocedure.do?reference=A9-0115/2021": "ficheprocedure_a9-0115-2021.html",
        "/oeil/popups/ficheprocedure.do?reference=A9-0149/2021": "ficheprocedure_a9-0149-2021.html",
        "/oeil/popups/ficheprocedure.do?reference=A8-0141/2019": "ficheprocedure_a9-0141-2019.html",
        "/oeil/popups/summary.do?id=1651118&t=e&l=en": "summary-1651118.html",
        "/oeil/srvc/calendar.json?y=2021&m=11": "calendar-2021-11.json",
    }

    if url not in MOCK_RESPONSES:
        context.status_code = 404
        return "No content"

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


def test_voting_lists_scraper_run_document_register_url_votings(mock_request):
    scraper = VotingListsScraper(term=8, date=date(2019, 3, 26))
    result = scraper.run()

    expected = [
        Voting(doceo_member_id=5682, name="Ali", position=Position.FOR),
        Voting(doceo_member_id=6407, name="Arthuis", position=Position.FOR),
        Voting(doceo_member_id=6097, name="van Baalen", position=Position.FOR),
        Voting(doceo_member_id=6110, name="Bearder", position=Position.FOR),
        Voting(
            doceo_member_id=6646, name="Becerra Basterrechea", position=Position.FOR
        ),
    ]

    assert result[0].votings[:5] == expected


def test_voting_lists_scraper_run_positions_missing(mock_request):
    scraper = VotingListsScraper(term=9, date=date(2019, 10, 22))

    votings = [
        Voting(doceo_member_id=5602, name="Ždanoka", position=Position.FOR),
        Voting(doceo_member_id=6752, name="Mobarik", position=Position.ABSTENTION),
    ]

    voting_lists = scraper.run()

    assert voting_lists[0].votings == votings


def test_voting_lists_scraper_voting_alternate_name():
    scraper = VotingListsScraper(term=9, date=date(2021, 1, 1))

    xml = '<Member.Name MepId="6644">Pagazaurtundúa Ruiz</Member.Name>'
    tag = BeautifulSoup(xml, "lxml-xml").find("Member.Name")

    expected = Voting(
        doceo_member_id=6644, name="Pagazaurtundúa", position=Position.FOR
    )
    actual = scraper._voting(tag, position=Position.FOR)

    assert actual == expected


def test_voting_lists_scraper_description_remove_date():
    scraper = VotingListsScraper(term=9, date=date(2021, 1, 1))

    xml = (
        "<RollCallVote.Description.Text>"
        "   Description 01/01/2021 12:34:56.000"
        "</RollCallVote.Description.Text>"
    )

    tag = BeautifulSoup(xml, "lxml-xml")

    expected = "Description"
    actual = scraper._description(tag)

    assert actual == expected


def test_vote_collections_scraper_url(mock_request):
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))

    expected_doceo = (
        "https://www.europarl.europa.eu/doceo/document/PV-9-2021-03-09-VOT_EN.xml"
    )
    expected_document_register = (
        "https://www.europarl.europa.eu/RegData/seance_pleniere/proces_verbal/"
        "2021/03-09/liste_presence/P9_PV(2021)03-09(VOT)_EN.xml"
    )
    assert scraper._url() == [expected_doceo, expected_document_register]


def test_vote_collections_scraper_run(mock_request):
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


def test_vote_collections_scraper_run_document_register_url_vote_items(mock_request):
    scraper = VoteCollectionsScraper(term=8, date=date(2019, 3, 26))
    result = scraper.run()
    assert len(result[17].votes) == 3

    expected_votes = [
        Vote(
            subject="§ 1, after point g",
            subheading=None,
            author="EFDD",
            result=VoteResult.REJECTED,
            split_part=None,
            amendment="1",
            type=VoteType.AMENDMENT,
            remarks="19044315",
        ),
        Vote(
            subject="§ 1, point m",
            subheading=None,
            author="Verts/ALE",
            result=VoteResult.REJECTED,
            split_part=None,
            amendment="3",
            type=VoteType.AMENDMENT,
            remarks="26435230",
        ),
        Vote(
            subject="Vote: recommendation (as a whole)",
            subheading=None,
            author=None,
            result=VoteResult.ADOPTED,
            split_part=None,
            amendment=None,
            type=VoteType.PRIMARY,
            remarks="39313281",
            final=True,
        ),
    ]

    assert result[17].votes == expected_votes


def test_vote_collections_scraper_run_doceo_url_vote_items(mock_request):
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
            final=True,
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


# The indication for lapsed votes is sometimes in the wrong column.
# https://www.europarl.europa.eu/doceo/document/PV-9-2021-06-07-VOT_EN.html No 24
def test_vote_collections_scraper_include_row_lapsed_in_remarks():
    scraper = VoteCollectionsScraper(term=9, date=date(2021, 3, 9))

    rows = [
        {
            "Subject": "B9-0317/2021",
            "Am No": "",
            "Author": "ID",
            "RCV etc.": "RCV",
            "Vote": "",
            "RCV/EV – remarks": "↓",
        }
    ]

    assert scraper._include_row(rows[0]) is False


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


def test_summary_id_scraper_run(mock_request):
    scraper = SummaryIDScraper(week_of_year=6, reference="B9-0116/2021")
    assert scraper.run() == "1651118"


def test_summary_id_scraper_run_no_summary(mock_request):
    scraper = SummaryIDScraper(week_of_year=20, reference="A9-0115/2021")
    with pytest.raises(ScrapingException):
        scraper.run()


def test_summary_id_scraper_run_multiple_candidates_in_same_week(mock_request):
    with pytest.raises(ScrapingException):
        SummaryIDScraper(week_of_year=20, reference="A9-0149/2021").run()


def test_summary_id_scraper_run_iso_week_numbers(mock_request):
    # It's important to use ISO-standard week numbers!
    scraper = SummaryIDScraper(week_of_year=13, reference="A8-0141/2019")
    assert scraper.run() == "1579841"


def test_summary_id_scraper_url(mock_request):
    scraper = SummaryIDScraper(week_of_year=6, reference="B9-0116/2021")
    expected = "https://oeil.secure.europarl.europa.eu/oeil/popups/ficheprocedure.do?reference=B9-0116/2021"

    assert scraper._url() == expected


def test_summary_id_scraper_is_summary_row_in_week(mock_request):
    scraper = SummaryIDScraper(week_of_year=6, reference="B9-0116/2021")

    html = "".join(
        [
            '<div class="ep-table-row">',
            '   <div class="ep-table-cell">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">27/01/2021</span>',
            "      </div>",
            "   </div>",
            '   <div class="ep-table-cell">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">Vote in committee, 1st reading</span>',
            "      </div>",
            "   </div>",
            "</div>",
            # This is the relevant row, as it contains the description "Decision by Parliament"
            '<div class="ep-table-row">',
            '   <div class="ep-table-cell ep-table-cell-s ep-table-column-head">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">09/02/2021</span>',
            "      </div>",
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-xl ep-table-column-head">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">Decision by Parliament, 1st reading</span>',
            "      </div>",
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-m center-cell">',
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-m center-cell">',
            '      <div class="ep-a_button ep-layout_neutral">',
            '         <div class="ep-p_button ep-p_smallbutton">',
            '            <button type="button" onclick="location.href=\'/oeil/popups/summary.do?id=1651043&amp;t=e&amp;l=en\'" title="Summary for Decision by Parliament, 1st reading" target="_blank">',
            '                <span class="ep_name">Summary</span><span class="ep_icon">&nbsp;</span>',
            "            </button>",
            "         </div>",
            "      </div>",
            "   </div>",
            "</div>",
        ]
    )

    rows = BeautifulSoup(html, "lxml-html").select(".ep-table-row")

    assert scraper._is_summary_row_in_week(rows[0]) is False
    assert scraper._is_summary_row_in_week(rows[1]) is True


def test_summary_id_scraper_is_summary_row_in_week_multiple_candidates(mock_request):
    scraper = SummaryIDScraper(week_of_year=6, reference="B9-0116/2021")

    html = "".join(
        [
            # This row contains a summary for another vote on a different date
            '<div class="ep-table-row">',
            '   <div class="ep-table-cell ep-table-cell-s ep-table-column-head">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">01/01/2021</span>',
            "      </div>",
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-xl ep-table-column-head">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">Decision by Parliament, 1st reading</span>',
            "      </div>",
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-m center-cell">',
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-m center-cell">',
            '      <div class="ep-a_button ep-layout_neutral">',
            '         <div class="ep-p_button ep-p_smallbutton">',
            '            <button type="button" onclick="location.href=\'/oeil/popups/summary.do?id=0000000&amp;t=e&amp;l=en\'" title="Summary for Decision by Parliament, 1st reading" target="_blank">',
            '                <span class="ep_name">Summary</span><span class="ep_icon">&nbsp;</span>',
            "            </button>",
            "         </div>",
            "      </div>",
            "   </div>",
            "</div>",
            # This is the relevant row, as description and date match
            '<div class="ep-table-row">',
            '   <div class="ep-table-cell ep-table-cell-s ep-table-column-head">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">09/02/2021</span>',
            "      </div>",
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-xl ep-table-column-head">',
            '      <div class="ep-p_text">',
            '         <span class="ep_name">Decision by Parliament, 2nd reading</span>',
            "      </div>",
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-m center-cell">',
            "   </div>",
            '   <div class="ep-table-cell ep-table-cell-m center-cell">',
            '      <div class="ep-a_button ep-layout_neutral">',
            '         <div class="ep-p_button ep-p_smallbutton">',
            '            <button type="button" onclick="location.href=\'/oeil/popups/summary.do?id=1234567&amp;t=e&amp;l=en\'" title="Summary for Decision by Parliament, 1st reading" target="_blank">',
            '                <span class="ep_name">Summary</span><span class="ep_icon">&nbsp;</span>',
            "            </button>",
            "         </div>",
            "      </div>",
            "   </div>",
            "</div>",
        ]
    )

    rows = BeautifulSoup(html, "lxml-html").select(".ep-table-row")

    assert scraper._is_summary_row_in_week(rows[0]) is False
    assert scraper._is_summary_row_in_week(rows[1]) is True


def test_summary_scraper_run(mock_request):
    scraper = SummaryScraper(summary_id="1651118")

    summary = "\n\n".join(
        [
            "The European Parliament adopted by 667 votes to 1, with 27 abstentions, a resolution on the situation in Myanmar.",
            "The text adopted in plenary had been tabled as a joint resolution by the EPP, S&D, Renew, Greens/EFA, ECR groups and The Left.",
            "On 1 February 2021, the military of Myanmar, known as the Tatmadaw, in a clear violation of the constitution of Myanmar, arrested President Win Myint and State Counsellor Aung San Suu Kyi, as well as leading members of the government, seized power over the legislative, judicial and executive branches of government through a coup d’état, and issued a one-year state of emergency.",
            "Parliament strongly condemns the military takeover and called on the Tatmadaw to immediately reinstate the civilian government, end the state of emergency, and allow all elected parliamentarians to assume their mandates in order to restore constitutional order and democratic norms.",
            "The resolution called for the immediate and unconditional release of President Win Myint, State Counsellor Aung San Suu Kyi, and all others who have been illegally arrested under the pretext of fake elections or fraudulent election results or other unfounded accusations that have no merit.",
            "Parliament urged the military and the rightfully elected Government of Myanmar under President Win Myint to initiate a free and fair process of drafting and implementing a new constitution together with the people of Myanmar, specifically guaranteeing the recognition and representation of all ethnic groups in Myanmar including the Rohingya, and that ensures security, freedom, harmony and peace for all.",
            "The resolution strongly criticised the restrictions on the freedom of expression and assembly, and in this light also strongly condemned the curtailing of media freedom through blacking out the internet and restricting and blocking social media platforms such as Facebook and Twitter.",
            "Parliament called on the EU institutions and other international financial organisations to closely scrutinise the financial activities of the Tatmadaw and its members and to elaborate on what kind of appropriate measures could be taken in case the situation in Myanmar fails to improve or even deteriorates further.",
            "The EU and its Member States are urged to:",
            "- increase pressure on the Tatmadaw and take any measure at their disposal to ensure the return to power of the elected authorities;",
            "- foster international coordination in order to prevent any unauthorised goods from being illegally exported from Myanmar, specifically benefiting the military economically, and to end the production of illegal goods, especially the exploitation of natural resources such as illegally harvested wood;",
            "- continue programmes that help the country’s citizens and to step up support where necessary in the light of the current crisis, including humanitarian assistance and democracy support initiatives.",
            "Parliament urged the Council to:",
            "- amend the mandate of the current scheme of restrictive measures to include breaches of democracy, and to extend targeted sanctions to the entire leadership of Myanmar’s military, including all those involved in the coup and other",
            "legal entities directly owned by those involved in the coup;",
            "- review, and possibly amend, the EU’s arms embargo on Myanmar to ensure that surveillance equipment and dual-use products that can be used by the military in its crackdown on rights and dissent are covered by the embargo.",
        ]
    )

    assert scraper.run() == summary


def test_summary_scraper_format_paragraph():
    scraper = SummaryScraper(summary_id="1651118")

    html = "".join(
        [
            '<p class="MsoNormal" style="font-weight:bold;text-align:justify">',
            '   <span lang="EN-GB">',
            "       This is a heading",
            "   </span>",
            "</p>",
        ]
    )

    tag = BeautifulSoup(html, "lxml").select_one("p")

    assert scraper._format_paragraph(tag) == "## This is a heading"


def test_sessions_scraper_run(mock_request):
    scraper = SessionsScraper(month=11, year=2021)
    result = scraper.run()

    session_one = Session(date(2021, 11, 10), date(2021, 11, 11), Location.BRUSSELS)
    session_two = Session(date(2021, 11, 22), date(2021, 11, 25), Location.STRASBOURG)

    assert result == [session_one, session_two]
