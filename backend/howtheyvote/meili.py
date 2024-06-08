import meilisearch
from meilisearch.index import Index
from structlog import get_logger

from . import config
from .models import BaseWithId, Vote

log = get_logger(__name__)

meili = meilisearch.Client(config.MEILI_URL or "", config.MEILI_MASTER_KEY)


def index_name(name: str) -> str:
    prefix = config.SEARCH_INDEX_PREFIX

    if not prefix:
        return name

    return f"{prefix}-{name}"


def get_index(model_cls: type[BaseWithId]) -> Index:
    name = index_name(model_cls.__table__.name)  # type: ignore

    if model_cls != Vote:
        raise ValueError(f'Cannot get index "{name}" for model "{model_cls.__name__}"')

    return meili.index(name)


votes_index = get_index(Vote)


def configure_indexes() -> None:
    uid = votes_index.uid

    """Configure Meilisearch indexes."""
    log.info("Creating index.", uid=uid)
    meili.create_index(uid, {"primaryKey": "id"})

    log.info("Updating index settings.", uid=uid)
    votes_index.update_displayed_attributes(
        [
            "id",
            "display_title",
            "timestamp",
            "reference",
            "procedure_reference",
            "description",
            "is_featured",
            "geo_areas",
        ]
    )
    votes_index.update_searchable_attributes(
        [
            "display_title",
            "reference",
            "procedure_reference",
            "geo_areas",
            "keywords",
        ]
    )
    votes_index.update_sortable_attributes(["id", "timestamp"])
    votes_index.update_filterable_attributes(["is_featured"])
    votes_index.update_typo_tolerance(
        {
            "disableOnAttributes": ["reference", "procedure_reference"],
        }
    )
    votes_index.update_ranking_rules(
        [
            "words",
            "typo",
            "proximity",
            "attribute",
            "sort",
            "exactness",
            # Promote featured and recent votes by default
            "timestamp:desc",
            "is_featured:desc",
        ]
    )


def delete_indexes() -> None:
    """Delete all Meilisearch indexes."""
    log.info("Deleting index", uid=votes_index.uid)
    votes_index.delete()
