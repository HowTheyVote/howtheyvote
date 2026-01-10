import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import BaseWithId
from .vote import Vote, VotePositionCounts


class OEILSummary(BaseWithId):
    __tablename__ = "oeil_summaries"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(sa.Date)
    procedure_reference: Mapped[str] = mapped_column(sa.Unicode)
    content: Mapped[str] = mapped_column(sa.Unicode)
    votes: Mapped[list[Vote]] = relationship(back_populates="oeil_summary")
    position_counts: Mapped[list[VotePositionCounts]] = mapped_column(
        sa.JSON(none_as_null=True)
    )
