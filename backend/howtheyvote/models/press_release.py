import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import BaseWithId
from .vote import Vote, VotePositionCounts


class PressRelease(BaseWithId):
    __tablename__ = "press_releases"

    id: Mapped[str] = mapped_column(sa.Unicode, primary_key=True)
    published_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime)
    title: Mapped[str] = mapped_column(sa.Unicode)
    term: Mapped[int] = mapped_column(sa.Integer)
    references: Mapped[list[str]] = mapped_column(sa.JSON)
    procedure_references: Mapped[list[str]] = mapped_column(sa.JSON)
    facts: Mapped[str] = mapped_column(sa.Unicode)
    text: Mapped[str] = mapped_column(sa.Unicode)
    position_counts: Mapped[list[VotePositionCounts]] = mapped_column(
        sa.JSON(none_as_null=True)
    )
    votes: Mapped[list[Vote]] = relationship(back_populates="press_release")
