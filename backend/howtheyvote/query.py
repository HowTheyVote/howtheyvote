import datetime
from collections.abc import Iterable

import sqlalchemy as sa
from sqlalchemy import ColumnElement, Exists, exists, func

from .models import BaseWithId, Fragment, Member, PlenarySession


def member_has_term(term: int) -> Exists:
    """Returns an expression that can be used to select only members for the given term."""
    exp = func.json_each(Member.terms).table_valued("value")
    return exists().select_from(exp).where(exp.c.value == term)


def member_active_at(date: datetime.date) -> Exists:
    """Returns an expression that can be used to select only members with an active group
    membership on the given date."""
    exp = func.json_each(Member.group_memberships).table_valued("value")
    start_date = func.date(func.json_extract(exp.c.value, "$.start_date"))
    end_date = func.date(func.json_extract(exp.c.value, "$.end_date"))

    return (
        exists()
        .select_from(exp)
        .where(
            sa.and_(
                start_date <= date,
                sa.or_(end_date == None, end_date >= date),  # noqa: E711
            )
        )
    )


def session_is_current_at(date: datetime.date) -> ColumnElement[bool]:
    """Returns an expression that can be used to select the plenary session for
    the given date."""
    return sa.and_(
        func.date(PlenarySession.start_date) <= func.date(date),
        func.date(PlenarySession.end_date) >= func.date(date),
    )


def fragments_for_records(records: Iterable[BaseWithId | None]) -> ColumnElement[bool]:
    """Returns an expression that can be used to select fragments for the given records."""
    filters: list[ColumnElement[bool]] = []

    for record in records:
        if not record:
            continue

        filters.append(
            sa.and_(
                Fragment.model == record.__class__.__name__,
                Fragment.group_key == record.id,
            ),
        )

    return sa.or_(*filters)
