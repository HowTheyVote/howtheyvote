import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common import BaseWithId
from .vote import Vote


class OEILSummary(BaseWithId):
    __tablename__ = "oeil_summaries"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    content: Mapped[str] = mapped_column(sa.Unicode)
    votes: Mapped[list[Vote]] = relationship(back_populates="oeil_summary")
