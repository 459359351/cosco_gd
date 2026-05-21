"""向已有库补种 sys_dict（迁移未跑或需重置时可用）。

用法（在 backend 目录）:
  python -m scripts.seed_sys_dict
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.sys_dict import SysDict

# 与迁移 20260521_0003 种子一致
SEED = [
    ("province", "广东", "广东", None, 1),
    ("province", "广西", "广西", None, 2),
    ("yard_type", "yard", "堆场", None, 1),
    ("yard_type", "logistics", "物流点", None, 2),
    ("yard_status", "normal", "正常", None, 1),
    ("yard_status", "busy", "繁忙", None, 2),
    ("yard_status", "warning", "预警", None, 3),
    ("cargo_category", "集装箱", "集装箱", None, 1),
    ("cargo_category", "散货", "散货", None, 2),
    ("cargo_category", "危险品", "危险品", None, 3),
    ("cargo_category", "件杂", "件杂", None, 4),
    ("alert_level", "info", "提示", None, 1),
    ("alert_level", "warning", "警告", None, 2),
    ("alert_level", "critical", "严重", None, 3),
    ("alert_type", "拥堵", "拥堵", None, 1),
    ("alert_type", "超容", "超容", None, 2),
    ("alert_type", "设备", "设备", None, 3),
    ("alert_type", "其它", "其它", None, 4),
    ("vehicle_status", "running", "在途", None, 1),
    ("vehicle_status", "idle", "空闲", None, 2),
    ("vehicle_status", "arrived", "已到达", None, 3),
]
CITIES = [
    *[( "city", c, c, "广东", i) for i, c in enumerate(["广州", "深圳", "佛山", "东莞", "珠海", "中山"], 1)],
    *[( "city", c, c, "广西", i) for i, c in enumerate(["南宁", "钦州", "北海", "防城港", "柳州"], 1)],
]


async def main() -> None:
    async with SessionLocal() as db:
        for dict_type, code, label, parent, sort_order in SEED + CITIES:
            exists = (
                await db.execute(
                    select(SysDict).where(SysDict.dict_type == dict_type, SysDict.code == code)
                )
            ).scalar_one_or_none()
            if exists:
                continue
            db.add(
                SysDict(
                    dict_type=dict_type,
                    code=code,
                    label=label,
                    parent_code=parent,
                    sort_order=sort_order,
                    enabled=True,
                )
            )
        await db.commit()
    print("sys_dict seed done.")


if __name__ == "__main__":
    asyncio.run(main())
