"""计算所有网点到本部（中远海运大厦）的直线距离，写入 repair_network_sites.distance。

使用 Haversine 公式计算球面距离，无需调用外部 API。

用法: 在 backend/ 目录下运行:
    python scripts/compute_distances.py
"""

import asyncio
import math
import sys

import asyncpg

DB_URL = "postgresql://postgres:postgres@localhost:5432/cosco_gd"

# 中远海运大厦（广东省广州市黄埔区港湾路139号）
HQ_LNG = 113.460136
HQ_LAT = 23.183564

# 地球半径（米）
EARTH_RADIUS = 6371000.0


def haversine(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """计算两点之间的球面距离（米）。"""
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (math.sin(dlat / 2) ** 2
         + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c


async def main():
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("计算网点 → 本部 直线距离（Haversine）")
    print("=" * 60)

    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch(
        "SELECT id, name, parent_name, lng, lat FROM repair_network_sites "
        "WHERE lng != 0 AND lat != 0 ORDER BY id"
    )
    print(f"\n总网点: {len(rows)}")

    updated = 0
    for r in rows:
        dist = haversine(r["lng"], r["lat"], HQ_LNG, HQ_LAT)
        await conn.execute(
            "UPDATE repair_network_sites SET distance = $1 WHERE id = $2",
            round(dist), r["id"],
        )
        updated += 1
        km = dist / 1000
        print(f"  {r['parent_name']:12s} / {r['name']:20s} → {km:>7.1f} km")

    # Verify
    total = await conn.fetchval("SELECT count(*) FROM repair_network_sites")
    with_dist = await conn.fetchval(
        "SELECT count(*) FROM repair_network_sites WHERE distance > 0"
    )

    print(f"\n完成! 更新 {updated} 条, 数据库总计 {total} 条, 有距离 {with_dist} 条")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
