from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CargoCategory(Base):
    __tablename__ = "cargo_category"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    yard_id: Mapped[int] = mapped_column(ForeignKey("yards.id"), index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    volume: Mapped[int] = mapped_column(Integer, default=0)
