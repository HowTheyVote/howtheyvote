from sqlalchemy import func, select

from howtheyvote.models import Fragment
from howtheyvote.store import BulkWriter

fragment_1 = Fragment(
    model="Test",
    source_name="foo",
    source_id="foo:1",
    group_key="1",
    data={},
)

fragment_2 = Fragment(
    model="Test",
    source_name="bar",
    source_id="bar:1",
    group_key="1",
    data={},
)

fragment_3 = Fragment(
    model="Test",
    source_name="baz",
    source_id="baz:1",
    group_key="1",
    data={},
)


def test_bulk_writer_add():
    # Individual fragments
    writer = BulkWriter()
    writer.add(fragment_1)
    assert len(writer.fragments) == 1
    assert fragment_1 in writer.fragments

    # Lists
    writer = BulkWriter()
    writer.add([fragment_1, fragment_2])
    assert len(writer.fragments) == 2

    # Generators
    writer = BulkWriter()
    writer.add(f for f in [fragment_1, fragment_2])
    assert len(writer.fragments) == 2


def test_bulk_writer_flush(db_session):
    writer = BulkWriter()
    writer.add(fragment_1)

    query = select(func.count()).select_from(Fragment)
    count = db_session.execute(query).scalar()
    assert count == 0

    writer.flush()
    count = db_session.execute(query).scalar()
    assert count == 1

    writer.add(fragment_2)
    writer.flush()
    count = db_session.execute(query).scalar()
    assert count == 2


def test_bulk_writer_auto_flush(db_session):
    writer = BulkWriter(auto_flush=2)
    writer.add([fragment_1, fragment_2, fragment_3])

    query = select(func.count()).select_from(Fragment)
    count = db_session.execute(query).scalar()
    assert count == 2

    writer.flush()
    query = select(func.count()).select_from(Fragment)
    count = db_session.execute(query).scalar()
    assert count == 3


def test_bulk_writer_upsert(db_session):
    before = Fragment(
        model="Test",
        source_name="foo",
        source_id="foo:1",
        group_key="1",
        data={"value": "before"},
    )

    after = Fragment(
        model="Test",
        source_name="foo",
        source_id="foo:1",
        group_key="1",
        data={"value": "after"},
    )

    writer = BulkWriter()
    writer.add(before)
    writer.flush()

    fragment = db_session.execute(select(Fragment)).scalar()
    assert fragment.data["value"] == "before"

    writer = BulkWriter()
    writer.add(after)
    writer.flush()

    fragment = db_session.execute(select(Fragment)).scalar()
    assert fragment.data["value"] == "after"


def test_bulk_writer_get_touched(db_session):
    fragment = Fragment(
        model="Test",
        source_name="foo",
        source_id="foo:1",
        group_key="1",
        data={},
    )

    writer = BulkWriter()

    assert writer.get_touched() == set()

    writer.add(fragment)
    writer.flush()

    assert writer.get_touched() == {"1"}
