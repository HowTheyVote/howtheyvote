from pathlib import Path
from typing import Any

from sqlalchemy.orm import DeclarativeBase

FIXTURES_BASE = Path(__file__).resolve().parent / "data"


def load_fixture(path: str) -> str:
    return FIXTURES_BASE.joinpath(path).read_text()


def record_to_dict(record: DeclarativeBase) -> dict[str, Any]:
    return {c.name: getattr(record, c.name) for c in record.__table__.columns}
