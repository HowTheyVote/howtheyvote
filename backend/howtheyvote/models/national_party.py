import dataclasses

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass


class NationalPartyMeta(type):
    def __getitem__(cls, key: str) -> "NationalParty":
        party = national_parties.get(key)

        if not party:
            raise KeyError()

        return party


@dataclasses.dataclass(frozen=True)
class NationalParty(DeserializableDataclass, metaclass=NationalPartyMeta):
    id: str
    short_label: str
    label: str
    start_date: str
    end_date: str | None
    country_code: str

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def get(cls, key: str) -> "NationalParty | None":
        try:
            return cls[key]
        except KeyError:
            return None


national_parties = DataclassContainer(
    dataclass=NationalParty,
    file_path=DATA_DIR.joinpath("national_parties.json"),
    key_attr="id",
)
national_parties.load()
