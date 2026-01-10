from ..models import Fragment
from .helpers import extract_vote_results


class OEILSummaryVotePositionCountsAnalyzer:
    """Extracts mentioned vote position counts from summary."""

    def __init__(self, summary_id: int, text: str):
        self.summary_id = summary_id
        self.text = text

    def run(self) -> Fragment | None:
        if not self.text:
            return None

        position_counts = extract_vote_results(self.text)

        if not position_counts:
            return None

        return Fragment(
            model="OEILSummary",
            source_id=self.summary_id,
            source_name=type(self).__name__,
            group_key=self.summary_id,
            data={"position_counts": position_counts},
        )
