from collections.abc import Iterable

from sqlalchemy.dialects.sqlite import insert
from structlog import get_logger

from ..db import Session
from ..helpers import chunks
from ..models import Fragment

log = get_logger(__name__)


class BulkWriter:
    """Writes `howtheyvote.models.Fragment`s to the database in bulk."""

    fragments: list[Fragment]
    """Buffer of fragments to be written to the database."""

    auto_flush: int | None
    """Automatically flush the writer if the buffer contains at least `auto_flush`
    fragments."""

    def __init__(self, auto_flush: int | None = None):
        self.fragments = []
        self.auto_flush = auto_flush
        self._touched: set[str] = set()

    def add(self, fragments: Iterable[Fragment] | Fragment | None) -> None:
        """Add a single fragment or a list of fragments to the bulk writer. Fragments are
        not written to the database until the `flush` method is called."""
        if not fragments:
            return

        if isinstance(fragments, Fragment):
            fragments = [fragments]

        if not self.auto_flush:
            self.fragments.extend(fragments)
            self._flush_if_necessary()
        else:
            for chunk in chunks(fragments, size=self.auto_flush):
                self.fragments.extend(chunk)
                self._flush_if_necessary()

    def flush(self) -> None:
        """Write all buffered fragments to the database in bulk."""
        upsert_fragments(self.fragments)
        self._touched.update(str(fragment.group_key) for fragment in self.fragments)

        self.fragments = []

    def get_touched(self) -> set[str]:
        """Returns list of fragment group keys that were written/updated."""
        return self._touched

    def _flush_if_necessary(self) -> None:
        if not self.auto_flush:
            return

        if len(self.fragments) >= self.auto_flush:
            log.info("Auto flushing fragments writer", count=len(self.fragments))
            self.flush()


def upsert_fragments(fragments: list[Fragment]) -> None:
    """Create or update a list of `howtheyvote.models.Fragment`s in the database."""
    if not fragments:
        log.info("Empty fragments list given, not inserting any fragments.")
        return

    values = []

    for fragment in fragments:
        values.append(
            {
                "model": fragment.model,
                "source_name": fragment.source_name,
                "source_id": fragment.source_id,
                "source_url": fragment.source_url,
                "group_key": fragment.group_key,
                "data": fragment.data,
            }
        )

    log.info("Inserting fragments.", count=len(fragments))
    stmt = insert(Fragment).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Fragment.model, Fragment.source_name, Fragment.source_id],
        set_={
            "source_url": stmt.excluded.source_url,
            "timestamp": stmt.excluded.timestamp,
            "data": stmt.excluded.data,
        },
    )

    Session.execute(stmt)
    Session.commit()
