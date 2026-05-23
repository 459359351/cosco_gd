from datetime import datetime

from sqlalchemy import (
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RepairWeeklyOrg(Base):
    __tablename__ = "repair_weekly_org"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    company_type: Mapped[str] = mapped_column(String(20), nullable=False)
    org_name: Mapped[str] = mapped_column(String(120), nullable=False)
    org_code: Mapped[str] = mapped_column(String(60), nullable=False)
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    container_qty: Mapped[int] = mapped_column(Integer, default=0)
    qty_wow_change: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0)
    rev_wow_change: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    move_fee: Mapped[float] = mapped_column(Float, default=0)
    total_qty: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0)
    per_capita: Mapped[float] = mapped_column(Float, default=0)
    staff_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint(
            "year", "week", "org_code", "customer_type",
            name="uq_repair_org_week_cust",
        ),
        Index("ix_repair_org_year_week", "year", "week"),
    )


class RepairWeeklySummary(Base):
    __tablename__ = "repair_weekly_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    summary_type: Mapped[str] = mapped_column(String(40), nullable=False)
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    container_qty: Mapped[int] = mapped_column(Integer, default=0)
    qty_wow_change: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0)
    rev_wow_change: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    move_fee: Mapped[float] = mapped_column(Float, default=0)
    total_qty: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0)
    per_capita: Mapped[float] = mapped_column(Float, default=0)
    staff_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint(
            "year", "week", "summary_type", "customer_type",
            name="uq_repair_summary_week_type_cust",
        ),
    )


class RepairWeeklySiteDetail(Base):
    __tablename__ = "repair_weekly_site_detail"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    site_name: Mapped[str] = mapped_column(String(120), nullable=False)
    company_name: Mapped[str] = mapped_column(String(120), nullable=False)
    company_type: Mapped[str] = mapped_column(String(20), nullable=False)
    container_class: Mapped[str] = mapped_column(String(40), default="")
    customer_name: Mapped[str] = mapped_column(String(60), default="")
    repair_qty: Mapped[int] = mapped_column(Integer, default=0)
    approved_amount: Mapped[float] = mapped_column(Float, default=0)
    move_fee: Mapped[float] = mapped_column(Float, default=0)

    __table_args__ = (
        Index("ix_repair_site_year_week", "year", "week"),
        Index("ix_repair_site_company", "company_name"),
        Index("ix_repair_site_type", "company_type"),
    )


class RepairWeeklyCumulative(Base):
    __tablename__ = "repair_weekly_cumulative"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    org_name: Mapped[str] = mapped_column(String(120), nullable=False)
    org_code: Mapped[str] = mapped_column(String(60), nullable=False)
    cum_qty: Mapped[int] = mapped_column(Integer, default=0)
    cum_qty_yoy: Mapped[int] = mapped_column(Integer, default=0)
    cum_revenue: Mapped[float] = mapped_column(Float, default=0)
    cum_revenue_yoy: Mapped[float] = mapped_column(Float, default=0)

    __table_args__ = (
        UniqueConstraint(
            "year", "week", "org_code",
            name="uq_repair_cum_week_org",
        ),
    )


class RepairNetworkSite(Base):
    __tablename__ = "repair_network_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    company_type: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_name: Mapped[str] = mapped_column(String(120), default="")
    parent_code: Mapped[str] = mapped_column(String(60), default="")
    province: Mapped[str] = mapped_column(String(40), default="")
    city: Mapped[str] = mapped_column(String(40), default="")
    lng: Mapped[float] = mapped_column(Float, default=0)
    lat: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")


class ExcelUploadLog(Base):
    __tablename__ = "excel_upload_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    row_counts: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
