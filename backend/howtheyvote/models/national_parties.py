import dataclasses

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass
from .country import Country


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
    alt_label: str | None
    # TODO: Fix type here?
    start_date: str | None
    end_date: str | None
    country_code: str | None

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def get(cls, key: str) -> "NationalParty | None":
        try:
            return cls[key]
        except KeyError:
            return None


# national_parties = DataclassContainer(
#     dataclass=NationalParty,
#     file_path=DATA_DIR.joinpath("national_parties.json"),
#     key_attr="id",
# )
# national_parties.load()


# class NationalPartyType(TypeDecorator[NationalParty]):
#     impl = sa.Unicode
#     cache_ok = True
#
#     def process_bind_param(self, value: NationalParty | None, dialect: Dialect) -> str | None:
#         if not value:
#             return None
#
#         return value.id
#
#     def process_result_value(
#         self, value: str | None, dialect: Dialect
#     ) -> NationalParty | None:
#         if not value:
#             return None
#
#         return national_parties.get(value)
#
