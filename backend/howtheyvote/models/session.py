import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .common import BaseWithId


class PlenarySessionLocation(Enum):
    """
    Locality of a plenary session
    """

    SXB = "SXB"
    BRU = "BRU"


class PlenarySessionStatus(Enum):
    CURRENT = "CURRENT"
    UPCOMING = "UPCOMING"
    PAST = "PAST"


class PlenarySession(BaseWithId):
    __tablename__ = "plenary_sessions"

    id: Mapped[str] = mapped_column(sa.Unicode, primary_key=True)
    term: Mapped[int] = mapped_column(sa.Integer)
    start_date: Mapped[datetime.date] = mapped_column(sa.Date)
    end_date: Mapped[datetime.date] = mapped_column(sa.Date)
    location: Mapped[PlenarySessionLocation | None] = mapped_column(
        sa.Enum(PlenarySessionLocation)
    )

    @property
    def status(self) -> PlenarySessionStatus:
        today = datetime.date.today()

        if self.start_date > today:
            return PlenarySessionStatus.UPCOMING

        if self.end_date < today:
            return PlenarySessionStatus.PAST

        return PlenarySessionStatus.CURRENT
