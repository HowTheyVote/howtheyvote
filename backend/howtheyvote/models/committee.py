import dataclasses
import datetime

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass
from .types import DataclassReferenceType


class CommitteeMeta(type):
    def __getitem__(cls, key: str) -> "Committee":
        committee = committees.get(key)

        if not committee:
            raise KeyError(f"No committee with code {key} found.")

        return committee


@dataclasses.dataclass(frozen=True)
class Committee(DeserializableDataclass, metaclass=CommitteeMeta):
    code: str
    official_label: str
    label: str
    abbreviation: str
    start_date: datetime.date
    end_date: datetime.date | None

    def __hash__(self) -> int:
        return hash(self.code)

    @classmethod
    def get(cls, key: str) -> "Committee | None":
        try:
            return cls[key]
        except KeyError:
            return None


committees = DataclassContainer(
    dataclass=Committee,
    file_path=DATA_DIR.joinpath("committees.json"),
    key_attr="code",
)
committees.load()


CommitteeType = DataclassReferenceType[Committee](committees)
