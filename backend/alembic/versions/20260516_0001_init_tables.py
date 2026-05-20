"""init tables

Revision ID: 20260516_0001
Revises:
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "20260516_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "yards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=60), nullable=False, unique=True),
        sa.Column("yard_type", sa.String(length=40), nullable=False),
        sa.Column("province", sa.String(length=40), nullable=False),
        sa.Column("city", sa.String(length=40), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326), nullable=True),
    )

    op.create_table(
        "throughput_daily",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("yard_id", sa.Integer(), sa.ForeignKey("yards.id"), index=True),
        sa.Column("stat_date", sa.Date(), index=True),
        sa.Column("in_teu", sa.Integer(), server_default="0"),
        sa.Column("out_teu", sa.Integer(), server_default="0"),
        sa.Column("stock_teu", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "cargo_category",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("yard_id", sa.Integer(), sa.ForeignKey("yards.id"), index=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("volume", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("yard_id", sa.Integer(), sa.ForeignKey("yards.id"), index=True),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("alert_type", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), unique=True, nullable=False),
        sa.Column("from_yard_code", sa.String(length=60), nullable=False),
        sa.Column("to_yard_code", sa.String(length=60), nullable=False),
        sa.Column("progress", sa.Float(), server_default="0"),
        sa.Column("status", sa.String(length=20), server_default="running"),
    )


def downgrade() -> None:
    op.drop_table("vehicles")
    op.drop_table("alerts")
    op.drop_table("cargo_category")
    op.drop_table("throughput_daily")
    op.drop_table("yards")
