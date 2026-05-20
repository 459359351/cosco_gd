"""add flow_od table

Revision ID: 20260517_0002
Revises: 20260516_0001
Create Date: 2026-05-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260517_0002"
down_revision = "20260516_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "flow_od",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("from_yard_code", sa.String(length=60), nullable=False),
        sa.Column("to_yard_code", sa.String(length=60), nullable=False),
        sa.Column("value_teu", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("from_yard_code", "to_yard_code", name="uq_flow_od_pair"),
    )
    op.create_index("ix_flow_od_from_yard_code", "flow_od", ["from_yard_code"], unique=False)
    op.create_index("ix_flow_od_to_yard_code", "flow_od", ["to_yard_code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_flow_od_to_yard_code", table_name="flow_od")
    op.drop_index("ix_flow_od_from_yard_code", table_name="flow_od")
    op.drop_table("flow_od")
