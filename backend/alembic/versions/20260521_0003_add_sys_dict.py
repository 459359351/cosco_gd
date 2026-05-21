"""add sys_dict table and seed defaults

Revision ID: 20260521_0003
Revises: 20260517_0002
Create Date: 2026-05-21
"""

from alembic import op
import sqlalchemy as sa

revision = "20260521_0003"
down_revision = "20260517_0002"
branch_labels = None
depends_on = None

sys_dict = sa.table(
    "sys_dict",
    sa.column("dict_type", sa.String),
    sa.column("code", sa.String),
    sa.column("label", sa.String),
    sa.column("parent_code", sa.String),
    sa.column("sort_order", sa.Integer),
    sa.column("enabled", sa.Boolean),
    sa.column("remark", sa.String),
)


def _seed_rows() -> list[dict]:
    rows: list[dict] = [
        {"dict_type": "province", "code": "广东", "label": "广东", "parent_code": None, "sort_order": 1, "enabled": True, "remark": None},
        {"dict_type": "province", "code": "广西", "label": "广西", "parent_code": None, "sort_order": 2, "enabled": True, "remark": None},
        {"dict_type": "yard_type", "code": "yard", "label": "堆场", "parent_code": None, "sort_order": 1, "enabled": True, "remark": None},
        {"dict_type": "yard_type", "code": "logistics", "label": "物流点", "parent_code": None, "sort_order": 2, "enabled": True, "remark": None},
        {"dict_type": "yard_status", "code": "normal", "label": "正常", "parent_code": None, "sort_order": 1, "enabled": True, "remark": None},
        {"dict_type": "yard_status", "code": "busy", "label": "繁忙", "parent_code": None, "sort_order": 2, "enabled": True, "remark": None},
        {"dict_type": "yard_status", "code": "warning", "label": "预警", "parent_code": None, "sort_order": 3, "enabled": True, "remark": None},
        {"dict_type": "cargo_category", "code": "集装箱", "label": "集装箱", "parent_code": None, "sort_order": 1, "enabled": True, "remark": None},
        {"dict_type": "cargo_category", "code": "散货", "label": "散货", "parent_code": None, "sort_order": 2, "enabled": True, "remark": None},
        {"dict_type": "cargo_category", "code": "危险品", "label": "危险品", "parent_code": None, "sort_order": 3, "enabled": True, "remark": None},
        {"dict_type": "cargo_category", "code": "件杂", "label": "件杂", "parent_code": None, "sort_order": 4, "enabled": True, "remark": None},
        {"dict_type": "alert_level", "code": "info", "label": "提示", "parent_code": None, "sort_order": 1, "enabled": True, "remark": None},
        {"dict_type": "alert_level", "code": "warning", "label": "警告", "parent_code": None, "sort_order": 2, "enabled": True, "remark": None},
        {"dict_type": "alert_level", "code": "critical", "label": "严重", "parent_code": None, "sort_order": 3, "enabled": True, "remark": None},
        {"dict_type": "alert_type", "code": "拥堵", "label": "拥堵", "parent_code": None, "sort_order": 1, "enabled": True, "remark": None},
        {"dict_type": "alert_type", "code": "超容", "label": "超容", "parent_code": None, "sort_order": 2, "enabled": True, "remark": None},
        {"dict_type": "alert_type", "code": "设备", "label": "设备", "parent_code": None, "sort_order": 3, "enabled": True, "remark": None},
        {"dict_type": "alert_type", "code": "其它", "label": "其它", "parent_code": None, "sort_order": 4, "enabled": True, "remark": None},
        {"dict_type": "vehicle_status", "code": "running", "label": "在途", "parent_code": None, "sort_order": 1, "enabled": True, "remark": None},
        {"dict_type": "vehicle_status", "code": "idle", "label": "空闲", "parent_code": None, "sort_order": 2, "enabled": True, "remark": None},
        {"dict_type": "vehicle_status", "code": "arrived", "label": "已到达", "parent_code": None, "sort_order": 3, "enabled": True, "remark": None},
    ]
    gd_cities = [
        ("广州", 1),
        ("深圳", 2),
        ("佛山", 3),
        ("东莞", 4),
        ("珠海", 5),
        ("中山", 6),
    ]
    gx_cities = [
        ("南宁", 1),
        ("钦州", 2),
        ("北海", 3),
        ("防城港", 4),
        ("柳州", 5),
    ]
    for name, order in gd_cities:
        rows.append(
            {
                "dict_type": "city",
                "code": name,
                "label": name,
                "parent_code": "广东",
                "sort_order": order,
                "enabled": True,
                "remark": None,
            }
        )
    for name, order in gx_cities:
        rows.append(
            {
                "dict_type": "city",
                "code": name,
                "label": name,
                "parent_code": "广西",
                "sort_order": order,
                "enabled": True,
                "remark": None,
            }
        )
    return rows


def upgrade() -> None:
    op.create_table(
        "sys_dict",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dict_type", sa.String(length=40), nullable=False),
        sa.Column("code", sa.String(length=60), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("parent_code", sa.String(length=60), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dict_type", "code", name="uq_sys_dict_type_code"),
    )
    op.create_index("ix_sys_dict_dict_type", "sys_dict", ["dict_type"], unique=False)
    op.create_index("ix_sys_dict_parent_code", "sys_dict", ["parent_code"], unique=False)
    op.bulk_insert(sys_dict, _seed_rows())


def downgrade() -> None:
    op.drop_index("ix_sys_dict_parent_code", table_name="sys_dict")
    op.drop_index("ix_sys_dict_dict_type", table_name="sys_dict")
    op.drop_table("sys_dict")
