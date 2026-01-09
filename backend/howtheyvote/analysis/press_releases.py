from ..models import Fragment
from .helpers import extract_vote_results


class PressReleaseVotePositionCountsAnalyzer:
    """Extracts mentioned vote position counts from press release text."""

    def __init__(self, release_id: str, text: str):
        self.release_id = release_id
        self.text = text

    def run(self) -> Fragment | None:
        if not self.text:
            return None

        position_counts = extract_vote_results(self.text)

        if not position_counts:
            return None

        return Fragment(
            model="PressRelease",
            source_id=self.release_id,
            source_name=type(self).__name__,
            group_key=self.release_id,
            data={"position_counts": position_counts},
        )
