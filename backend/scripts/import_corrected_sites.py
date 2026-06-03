"""将 corrected_sites.json 中的全量网点数据（含外包公司）写入 repair_network_sites 表。

用法: 在 backend/ 目录下运行:
    python scripts/import_corrected_sites.py
"""

import asyncio
import json
import re
import sys
from pathlib import Path

import asyncpg

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
DATA_FILE = BACKEND_DIR / "corrected_sites.json"
DB_URL = "postgresql://postgres:postgres@localhost:5432/cosco_gd"

# 自营运营中心清单 —— 其余 parent_name 均视为外包
SELF_PARENTS = {
    "珠三角运营中心",
    "北部湾运营中心",
    "广州运营中心",
    "深圳运营中心",
    "粤西运营中心",
    "南岗分公司",
}


def make_code(text: str) -> str:
    """生成 parent_code：去除非文字字符。"""
    return re.sub(r"[^\w一-鿿]", "", text)


def classify_company_type(parent_name: str) -> str:
    return "self" if parent_name in SELF_PARENTS else "outsourced"


async def upsert_sites(conn: asyncpg.Connection, sites: list[dict]) -> dict:
    stats = {"inserted": 0, "updated": 0, "failed": 0}

    for site in sites:
        code = site["code"]
        name = site["name"]
        company_type = site["company_type"]
        parent_name = site["parent_name"]
        parent_code = make_code(parent_name)
        province = site.get("province", "")
        city = site.get("city", "")
        lng = site.get("lng", 0.0)
        lat = site.get("lat", 0.0)

        try:
            existing = await conn.fetchrow(
                "SELECT id FROM repair_network_sites WHERE code = $1 AND name = $2",
                code,
                name,
            )
            if existing:
                await conn.execute(
                    """
                    UPDATE repair_network_sites SET
                        company_type = $1, parent_name = $2, parent_code = $3,
                        province = $4, city = $5, lng = $6, lat = $7, status = 'active'
                    WHERE id = $8
                    """,
                    company_type,
                    parent_name,
                    parent_code,
                    province,
                    city,
                    lng,
                    lat,
                    existing["id"],
                )
                stats["updated"] += 1
            else:
                await conn.execute(
                    """
                    INSERT INTO repair_network_sites
                        (name, code, company_type, parent_name, parent_code,
                         province, city, lng, lat, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'active')
                    """,
                    name,
                    code,
                    company_type,
                    parent_name,
                    parent_code,
                    province,
                    city,
                    lng,
                    lat,
                )
                stats["inserted"] += 1
                print(f"  + INSERT [{company_type}] {parent_name} / {name}")

        except Exception as e:
            print(f"  ✗ DB Error [{code} {name}]: {e}")
            stats["failed"] += 1

    return stats


async def main():
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("导入 corrected_sites.json → repair_network_sites")
    print("=" * 60)

    # 1. 读取数据
    if not DATA_FILE.exists():
        print(f"[ERROR] 数据文件不存在: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    print(f"\n数据文件: {len(raw)} 条记录")

    # 2. 补充 company_type
    sites = []
    for item in raw:
        item["company_type"] = classify_company_type(item["parent_name"])
        sites.append(item)

    self_count = sum(1 for s in sites if s["company_type"] == "self")
    out_count = sum(1 for s in sites if s["company_type"] == "outsourced")
    print(f"  自营: {self_count}, 外包: {out_count}")

    # 3. 写入数据库
    print("\n开始写入数据库...")
    conn = await asyncpg.connect(DB_URL)
    try:
        stats = await upsert_sites(conn, sites)
        print(f"\n完成! 新增: {stats['inserted']}, 更新: {stats['updated']}, 失败: {stats['failed']}")
    finally:
        await conn.close()

    # 4. 验证
    conn = await asyncpg.connect(DB_URL)
    try:
        total = await conn.fetchval("SELECT count(*) FROM repair_network_sites")
        out_total = await conn.fetchval(
            "SELECT count(*) FROM repair_network_sites WHERE company_type = 'outsourced'"
        )
        no_coords = await conn.fetchval(
            "SELECT count(*) FROM repair_network_sites WHERE lng = 0 OR lat = 0"
        )
        print(f"\n数据库验证: 总计 {total} 条, 外包 {out_total} 条, 无坐标 {no_coords} 条")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
