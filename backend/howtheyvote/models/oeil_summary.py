import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .common import BaseWithId


class OEILSummary(BaseWithId):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    content: Mapped[str] = mapped_column(sa.Unicode)
