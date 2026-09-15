from collections.abc import Iterator

import sqlalchemy as sa

from . import config


def list_spelling_variations(max_level: int) -> Iterator[tuple[str, str]]:
    """List pairs of words that are spelling variations of one another. For the different
    values of `max_level` see https://github.com/en-wl/wordlist#variant-level."""
    engine = sa.create_engine(config.SCOWL_DATABASE_URI)
    query = sa.text(
        """
        SELECT distinct LOWER(a.word) as word1, LOWER(b.word) as word2
        FROM words_w_variant_info AS a
        JOIN words_w_variant_info AS b USING (group_id, pos)
        WHERE a.word != b.word
        AND a.variant_level <= :max_level
        AND b.variant_level <= :max_level
        """
    )

    with engine.connect() as connection:
        yield from connection.execute(query, {"max_level": max_level}).tuples()
