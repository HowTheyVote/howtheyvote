from typing import Any

from sqlalchemy.orm import DeclarativeBase


def record_to_dict(record: DeclarativeBase) -> dict[str, Any]:
    return {c.name: getattr(record, c.name) for c in record.__table__.columns}
