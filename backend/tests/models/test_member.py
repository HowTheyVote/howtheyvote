import datetime

from sqlalchemy import Column, MetaData, Table, create_engine, select, text

from howtheyvote.models import Group, GroupMembership
from howtheyvote.models.member import GroupMembershipType
from howtheyvote.models.types import ListType


def test_group_membership_type():
    engine = create_engine("sqlite://")
    metadata = MetaData()

    table = Table(
        "members",
        metadata,
        Column("group_memberships", ListType(GroupMembershipType)),
    )

    group_memberships = [
        GroupMembership(
            term=9,
            group=Group["EPP"],
            start_date=datetime.date(2023, 1, 1),
            end_date=None,
        )
    ]

    with engine.connect() as connection:
        metadata.create_all(connection)
        stmt = table.insert().values(group_memberships=group_memberships)
        connection.execute(stmt)
        connection.commit()

        stmt = text("SELECT group_memberships from members")
        unprocessed = connection.execute(stmt).scalar()
        assert (
            unprocessed
            == '[{"term": 9, "start_date": "2023-01-01", "end_date": null, "group": "EPP"}]'
        )

        stmt = select(table)
        processed = connection.execute(stmt).scalar()
        assert processed == group_memberships
