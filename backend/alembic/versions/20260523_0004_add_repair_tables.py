"""add repair business tables

Revision ID: 20260523_0004
Revises: 20260521_0003
Create Date: 2026-05-23
"""

from alembic import op
import sqlalchemy as sa

revision = "20260523_0004"
down_revision = "20260521_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. repair_weekly_org — 机构级周报数据
    op.create_table(
        "repair_weekly_org",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("company_type", sa.String(20), nullable=False),
        sa.Column("org_name", sa.String(120), nullable=False),
        sa.Column("org_code", sa.String(60), nullable=False),
        sa.Column("customer_type", sa.String(20), nullable=False),
        sa.Column("container_qty", sa.Integer(), server_default="0"),
        sa.Column("qty_wow_change", sa.Integer(), server_default="0"),
        sa.Column("revenue", sa.Float(), server_default="0"),
        sa.Column("rev_wow_change", sa.Float(), server_default="0"),
        sa.Column("unit_price", sa.Float(), server_default="0"),
        sa.Column("move_fee", sa.Float(), server_default="0"),
        sa.Column("total_qty", sa.Integer(), server_default="0"),
        sa.Column("total_revenue", sa.Float(), server_default="0"),
        sa.Column("per_capita", sa.Float(), server_default="0"),
        sa.Column("staff_count", sa.Integer(), server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "week", "org_code", "customer_type", name="uq_repair_org_week_cust"),
    )
    op.create_index("ix_repair_org_year_week", "repair_weekly_org", ["year", "week"])

    # 2. repair_weekly_summary — 汇总行
    op.create_table(
        "repair_weekly_summary",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("summary_type", sa.String(40), nullable=False),
        sa.Column("customer_type", sa.String(20), nullable=False),
        sa.Column("container_qty", sa.Integer(), server_default="0"),
        sa.Column("qty_wow_change", sa.Integer(), server_default="0"),
        sa.Column("revenue", sa.Float(), server_default="0"),
        sa.Column("rev_wow_change", sa.Float(), server_default="0"),
        sa.Column("unit_price", sa.Float(), server_default="0"),
        sa.Column("move_fee", sa.Float(), server_default="0"),
        sa.Column("total_qty", sa.Integer(), server_default="0"),
        sa.Column("total_revenue", sa.Float(), server_default="0"),
        sa.Column("per_capita", sa.Float(), server_default="0"),
        sa.Column("staff_count", sa.Integer(), server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "week", "summary_type", "customer_type", name="uq_repair_summary_week_type_cust"),
    )

    # 3. repair_weekly_site_detail — 网点级明细
    op.create_table(
        "repair_weekly_site_detail",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("site_name", sa.String(120), nullable=False),
        sa.Column("company_name", sa.String(120), nullable=False),
        sa.Column("company_type", sa.String(20), nullable=False),
        sa.Column("container_class", sa.String(40), server_default=""),
        sa.Column("customer_name", sa.String(60), server_default=""),
        sa.Column("repair_qty", sa.Integer(), server_default="0"),
        sa.Column("approved_amount", sa.Float(), server_default="0"),
        sa.Column("move_fee", sa.Float(), server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_repair_site_year_week", "repair_weekly_site_detail", ["year", "week"])
    op.create_index("ix_repair_site_company", "repair_weekly_site_detail", ["company_name"])
    op.create_index("ix_repair_site_type", "repair_weekly_site_detail", ["company_type"])

    # 4. repair_weekly_cumulative — 周累计数据
    op.create_table(
        "repair_weekly_cumulative",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("org_name", sa.String(120), nullable=False),
        sa.Column("org_code", sa.String(60), nullable=False),
        sa.Column("cum_qty", sa.Integer(), server_default="0"),
        sa.Column("cum_qty_yoy", sa.Integer(), server_default="0"),
        sa.Column("cum_revenue", sa.Float(), server_default="0"),
        sa.Column("cum_revenue_yoy", sa.Float(), server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "week", "org_code", name="uq_repair_cum_week_org"),
    )

    # 5. repair_network_sites — 网点主数据
    op.create_table(
        "repair_network_sites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("code", sa.String(60), nullable=False),
        sa.Column("company_type", sa.String(20), nullable=False),
        sa.Column("parent_name", sa.String(120), server_default=""),
        sa.Column("parent_code", sa.String(60), server_default=""),
        sa.Column("province", sa.String(40), server_default=""),
        sa.Column("city", sa.String(40), server_default=""),
        sa.Column("lng", sa.Float(), server_default="0"),
        sa.Column("lat", sa.Float(), server_default="0"),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # 6. excel_upload_log — 上传日志
    op.create_table(
        "excel_upload_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(255), server_default=""),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("row_counts", sa.Text(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("excel_upload_log")
    op.drop_table("repair_network_sites")
    op.drop_table("repair_weekly_cumulative")
    op.drop_index("ix_repair_site_type", table_name="repair_weekly_site_detail")
    op.drop_index("ix_repair_site_company", table_name="repair_weekly_site_detail")
    op.drop_index("ix_repair_site_year_week", table_name="repair_weekly_site_detail")
    op.drop_table("repair_weekly_site_detail")
    op.drop_table("repair_weekly_summary")
    op.drop_index("ix_repair_org_year_week", table_name="repair_weekly_org")
    op.drop_table("repair_weekly_org")
