import datetime
from enum import Enum
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseWithId(Base):
    __abstract__ = True

    id: Mapped[str | int]


class Fragment(Base):
    __tablename__ = "fragments"

    model: Mapped[str] = mapped_column(sa.Unicode, primary_key=True)
    source_name: Mapped[str] = mapped_column(sa.Unicode, primary_key=True)
    source_id: Mapped[str] = mapped_column(sa.Unicode, primary_key=True)
    source_url: Mapped[str | None] = mapped_column(sa.Unicode)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    group_key: Mapped[str] = mapped_column(sa.Unicode)
    data: Mapped[dict[Any, Any]] = mapped_column(sa.JSON)


class PipelineStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    DATA_UNCHANGED = "DATA_UNCHANGED"


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime)
    finished_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime)
    pipeline: Mapped[str] = mapped_column(sa.Unicode)
    status: Mapped[PipelineStatus] = mapped_column(sa.Enum(PipelineStatus))
    checksum: Mapped[str] = mapped_column(sa.Unicode)
    idempotency_key: Mapped[str] = mapped_column(sa.Unicode)
