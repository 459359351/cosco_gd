from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.cargo import CargoCategory
from app.models.flow_od import FlowOD
from app.models.throughput import ThroughputDaily
from app.models.vehicle import Vehicle
from app.models.yard import Yard
from app.services.cache import get_cache, set_cache
from app.services.mock_data import (
    mock_alerts,
    mock_cargo_distribution,
    mock_flow,
    mock_trend,
    mock_yards,
)


async def list_yards(db: AsyncSession, province: str | None = None) -> list[dict]:
    cache_key = f"yards:{province or 'all'}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    result = await db.execute(select(Yard))
    rows = [row[0] for row in result.fetchall()]
    yards = []
    for row in rows:
        if province and row.province != province:
            continue
        yards.append(
            {
                "id": row.id,
                "name": row.name,
                "code": row.code,
                "yard_type": row.yard_type,
                "province": row.province,
                "city": row.city,
                "lng": row.lng,
                "lat": row.lat,
                "capacity": row.capacity,
                "status": row.status,
            }
        )
    if not yards:
        yards = [y for y in mock_yards() if province is None or y["province"] == province]

    await set_cache(cache_key, yards, ttl=60)
    return yards


async def yard_detail(db: AsyncSession, yard_id: int) -> dict | None:
    yards = await list_yards(db)
    yard = next((item for item in yards if item["id"] == yard_id), None)
    if not yard:
        return None
    return {
        "yard": yard,
        "today_in_teu": 320,
        "today_out_teu": 300,
        "stock_teu": 4500,
    }


async def kpi_overview(db: AsyncSession) -> dict:
    cache_key = "kpi:overview"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    yard_count = (await db.execute(select(func.count(Yard.id)))).scalar() or 0
    total_stock_teu = (await db.execute(select(func.sum(ThroughputDaily.stock_teu)))).scalar() or 0
    in_transit_vehicles = (
        await db.execute(select(func.count(Vehicle.id)).where(Vehicle.status == "running"))
    ).scalar() or 0
    today_throughput = (
        await db.execute(select(func.sum(ThroughputDaily.in_teu + ThroughputDaily.out_teu)))
    ).scalar() or 0

    if yard_count == 0:
        payload = {
            "yard_count": len(mock_yards()),
            "total_stock_teu": 11800,
            "today_throughput": 1620,
            "in_transit_vehicles": 68,
        }
    else:
        payload = {
            "yard_count": yard_count,
            "total_stock_teu": int(total_stock_teu),
            "today_throughput": int(today_throughput),
            "in_transit_vehicles": int(in_transit_vehicles),
        }
    await set_cache(cache_key, payload, ttl=20)
    return payload


async def throughput_trend(db: AsyncSession, days: int = 7) -> dict:
    cache_key = f"throughput:trend:{days}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    query = select(ThroughputDaily).order_by(ThroughputDaily.stat_date.desc()).limit(days)
    rows = [item[0] for item in (await db.execute(query)).fetchall()]
    if not rows:
        payload = {"points": mock_trend(days)}
    else:
        points = []
        for row in reversed(rows):
            points.append(
                {
                    "date": row.stat_date.isoformat(),
                    "in_teu": row.in_teu,
                    "out_teu": row.out_teu,
                    "stock_teu": row.stock_teu,
                }
            )
        payload = {"points": points}

    await set_cache(cache_key, payload, ttl=30)
    return payload


async def cargo_distribution(db: AsyncSession) -> dict:
    cache_key = "cargo:distribution"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    rows = [item[0] for item in (await db.execute(select(CargoCategory))).fetchall()]
    if not rows:
        payload = {"items": mock_cargo_distribution()}
    else:
        grouped = defaultdict(int)
        for row in rows:
            grouped[row.category] += row.volume
        payload = {"items": [{"category": k, "volume": v} for k, v in grouped.items()]}
    await set_cache(cache_key, payload, ttl=30)
    return payload


async def ranking_yards(db: AsyncSession, top: int = 10, province: str | None = None) -> dict:
    yards = await list_yards(db, province=province)
    ranking = sorted(yards, key=lambda item: item["capacity"], reverse=True)[:top]
    return {"items": ranking}


async def recent_alerts(db: AsyncSession) -> dict:
    rows = [item[0] for item in (await db.execute(select(Alert).order_by(Alert.created_at.desc()).limit(20))).fetchall()]
    if not rows:
        return {"items": mock_alerts()}
    return {
        "items": [
            {
                "id": row.id,
                "yard_id": row.yard_id,
                "level": row.level,
                "alert_type": row.alert_type,
                "message": row.message,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
    }


async def od_flow(db: AsyncSession) -> dict:
    result = await db.execute(select(FlowOD).order_by(FlowOD.id))
    rows = result.scalars().all()
    if not rows:
        return {"items": mock_flow()}
    return {
        "items": [
            {"from_code": r.from_yard_code, "to_code": r.to_yard_code, "value": r.value_teu}
            for r in rows
        ]
    }
