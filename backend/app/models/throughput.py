from datetime import date

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ThroughputDaily(Base):
    __tablename__ = "throughput_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    yard_id: Mapped[int] = mapped_column(ForeignKey("yards.id"), index=True)
    stat_date: Mapped[date] = mapped_column(Date, index=True)
    in_teu: Mapped[int] = mapped_column(Integer, default=0)
    out_teu: Mapped[int] = mapped_column(Integer, default=0)
    stock_teu: Mapped[int] = mapped_column(Integer, default=0)
