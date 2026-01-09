from howtheyvote.analysis.oeil_summaries import OEILSummaryVotePositionCountsAnalyzer
from howtheyvote.models import Fragment

from ..helpers import record_to_dict


def test_vote_position_counts_analyzer():
    analyzer = OEILSummaryVotePositionCountsAnalyzer(
        summary_id="1881375",
        text="The European Parliament adopted by 450 votes to 93, with 37 abstentions, a resolution.",
    )
    expected = Fragment(
        model="OEILSummary",
        source_id="1881375",
        source_name="OEILSummaryVotePositionCountsAnalyzer",
        group_key="1881375",
        data={
            "position_counts": [
                {
                    "FOR": 450,
                    "AGAINST": 93,
                    "ABSTENTION": 37,
                    "DID_NOT_VOTE": 0,
                },
            ],
        },
    )
    assert record_to_dict(analyzer.run()) == record_to_dict(expected)


def test_vote_position_counts_analyzer_multiple_counts():
    analyzer = OEILSummaryVotePositionCountsAnalyzer(
        summary_id="1720854",
        text="The European Parliament decided by 345 votes to 284, with 8 abstentions, to refuse to grant discharge for the financial year 2020. Parliament adopted a resolution with 467 votes to 136, with 15 abstentions, containing a series of recommendations.",
    )
    expected = Fragment(
        model="OEILSummary",
        source_id="1720854",
        source_name="OEILSummaryVotePositionCountsAnalyzer",
        group_key="1720854",
        data={
            "position_counts": [
                {
                    "FOR": 345,
                    "AGAINST": 284,
                    "ABSTENTION": 8,
                    "DID_NOT_VOTE": 0,
                },
                {
                    "FOR": 467,
                    "AGAINST": 136,
                    "ABSTENTION": 15,
                    "DID_NOT_VOTE": 0,
                },
            ],
        },
    )
    assert record_to_dict(analyzer.run()) == record_to_dict(expected)
