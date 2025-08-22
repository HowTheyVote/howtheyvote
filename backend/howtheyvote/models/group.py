import dataclasses
import datetime
from typing import Any

from unidecode import unidecode

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass


class GroupMeta(type):
    def __getitem__(cls, key: str) -> "Group":
        country = groups.get(key)

        if not country:
            raise KeyError()

        return country


@dataclasses.dataclass(frozen=True)
class Group(DeserializableDataclass, metaclass=GroupMeta):
    code: str
    official_label: str
    label: str
    short_label: str
    alt_labels: list[str]
    start_date: datetime.date
    end_date: datetime.date | None

    @classmethod
    def get(cls, key: str) -> "Group | None":
        try:
            return cls[key]
        except KeyError:
            return None

    @classmethod
    def from_label(cls, label: str, date: datetime.date | None = None) -> "Group | None":
        normalized = _normalize_label(label)

        for group in groups:
            # In some cases, there are multiple groups with identical names that were active
            # during different periods of time. In these cases, providing a date can help
            # disambiguate the groups.
            if date and (
                (group.start_date > date)
                or (group.end_date is not None and group.end_date < date)
            ):
                continue

            all_labels = [
                group.label,
                group.official_label,
                group.short_label,
                *group.alt_labels,
            ]
            all_normalized = set(_normalize_label(label) for label in all_labels if label)

            if normalized in all_normalized:
                return group

        return None

    @classmethod
    def from_dict(cls, data: dict[Any, Any]) -> "Group":
        data = {
            **data,
            "start_date": datetime.date.fromisoformat(data["start_date"]),
            "end_date": datetime.date.fromisoformat(data["end_date"])
            if data.get("end_date")
            else None,
        }

        return cls(**data)

    def __hash__(self) -> int:
        return hash(self.code)


groups = DataclassContainer(
    dataclass=Group,
    file_path=DATA_DIR.joinpath("groups.json"),
    key_attr="code",
)
groups.load()


def _normalize_label(label: str) -> str:
    normalized = unidecode(label.lower())
    normalized = normalized.removeprefix("group of the ")
    normalized = normalized.removesuffix(" group")
    return normalized
