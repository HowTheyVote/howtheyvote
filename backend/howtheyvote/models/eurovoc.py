import dataclasses

import sqlalchemy as sa
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from ..data import DATA_DIR, DataclassContainer, DeserializableDataclass
from .country import Country


class EurovocConceptMeta(type):
    def __getitem__(cls, key: str) -> "EurovocConcept":
        concept = eurovoc_concepts.get(key)

        if not concept:
            raise KeyError()

        return concept


@dataclasses.dataclass(frozen=True)
class EurovocConcept(DeserializableDataclass, metaclass=EurovocConceptMeta):
    id: str
    label: str
    alt_labels: set[str]
    related_ids: set[str]
    broader_ids: set[str]
    geo_area_code: str | None

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def get(cls, key: str) -> "EurovocConcept | None":
        try:
            return cls[key]
        except KeyError:
            return None

    @property
    def related(self) -> set["EurovocConcept"]:
        return {EurovocConcept[id_] for id_ in self.related_ids}

    @property
    def broader(self) -> set["EurovocConcept"]:
        return {EurovocConcept[id_] for id_ in self.broader_ids}

    @property
    def geo_area(self) -> Country | None:
        if not self.geo_area_code:
            return None

        return Country.get(self.geo_area_code)


eurovoc_concepts = DataclassContainer(
    dataclass=EurovocConcept,
    file_path=DATA_DIR.joinpath("eurovoc.json"),
    key_attr="id",
)
eurovoc_concepts.load()


class EurovocConceptType(TypeDecorator[EurovocConcept]):
    impl = sa.Unicode
    cache_ok = True

    def process_bind_param(self, value: EurovocConcept | None, dialect: Dialect) -> str | None:
        if not value:
            return None

        return value.id

    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> EurovocConcept | None:
        if not value:
            return None

        return eurovoc_concepts.get(value)
