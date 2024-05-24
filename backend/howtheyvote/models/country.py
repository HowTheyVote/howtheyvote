import dataclasses
import re

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass


class CountryMeta(type):
    def __getitem__(cls, key: str) -> "Country":
        country = countries.get(key)

        if not country:
            raise KeyError()

        return country


@dataclasses.dataclass(frozen=True)
class Country(DeserializableDataclass, metaclass=CountryMeta):
    code: str
    label: str
    alt_label: str | None
    iso_alpha_2: str | None

    @classmethod
    def get(cls, key: str) -> "Country | None":
        try:
            return cls[key]
        except KeyError:
            return None

    @classmethod
    def from_label(cls, label: str, fuzzy: bool = False) -> "Country | None":
        fuzzy_matches = []
        normalized = _normalize_label(label)

        for country in countries:
            if country.label == label:
                return country
            if country.alt_label == label:
                return country
            if _normalize_label(country.label).startswith(normalized):
                fuzzy_matches.append(country)
            if normalized.startswith(_normalize_label(country.label)):
                fuzzy_matches.append(country)

        if fuzzy and fuzzy_matches:
            return fuzzy_matches[0]

        return None

    def __hash__(self) -> int:
        return hash(self.code)


countries = DataclassContainer(
    dataclass=Country,
    file_path=DATA_DIR.joinpath("countries.json"),
    key_attr="code",
)
countries.load()


def _normalize_label(label: str) -> str:
    normalized = label.lower()
    normalized = re.sub(r"[^a-z\s\-]", "", normalized)

    return normalized


class CountryType(TypeDecorator[Country]):
    impl = sa.Unicode
    cache_ok = True

    def process_bind_param(self, value: Country | None, dialect: Dialect) -> str | None:
        if not value:
            return None

        return value.code

    def process_result_value(self, value: str | None, dialect: Dialect) -> Country | None:
        if not value:
            return None

        return Country[value]
