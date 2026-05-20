from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FlowOD(Base):
    """堆场间 OD 飞线强度（示例/种子数据；生产可由 ETL 写入）。"""

    __tablename__ = "flow_od"
    __table_args__ = (UniqueConstraint("from_yard_code", "to_yard_code", name="uq_flow_od_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_yard_code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    to_yard_code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    value_teu: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
