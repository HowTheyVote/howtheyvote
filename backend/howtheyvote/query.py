import datetime
from collections.abc import Iterable

import sqlalchemy as sa
from sqlalchemy import ColumnElement, Exists, exists, func

from .models import BaseWithId, Fragment, Member, PlenarySession, PressRelease, Vote


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


def press_release_references_vote(vote: Vote) -> ColumnElement[bool]:
    """Returns an expression that can be used to select press releases for a given vote,
    i.e. press releases published on the same date that reference the same procedure or
    report/resolution."""
    ref_exp = func.json_each(PressRelease.references).table_valued("value")
    proc_ref_exp = func.json_each(PressRelease.procedure_references).table_valued("value")

    return sa.and_(
        func.date(PressRelease.published_at) == vote.timestamp.date(),
        sa.or_(
            exists().select_from(ref_exp).where(ref_exp.c.value == vote.reference),
            exists()
            .select_from(proc_ref_exp)
            .where(proc_ref_exp.c.value == vote.procedure_reference),
        ),
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
