import asyncio
from datetime import date, datetime, timedelta
import random

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models.alert import Alert
from app.models.cargo import CargoCategory
from app.models.flow_od import FlowOD
from app.models.throughput import ThroughputDaily
from app.models.vehicle import Vehicle
from app.models.yard import Yard
from app.services.mock_data import mock_flow

SEED_YARDS = [
    {"name": "南沙港堆场A", "code": "GD-NSA-001", "yard_type": "yard", "province": "广东", "city": "广州", "lng": 113.6318, "lat": 22.7714, "capacity": 15000, "status": "normal"},
    {"name": "南沙港堆场B", "code": "GD-NSA-002", "yard_type": "yard", "province": "广东", "city": "广州", "lng": 113.6452, "lat": 22.7608, "capacity": 13000, "status": "busy"},
    {"name": "深圳盐田物流点", "code": "GD-SZ-001", "yard_type": "logistics", "province": "广东", "city": "深圳", "lng": 114.2580, "lat": 22.5860, "capacity": 12000, "status": "busy"},
    {"name": "蛇口联运站", "code": "GD-SZ-002", "yard_type": "logistics", "province": "广东", "city": "深圳", "lng": 113.9050, "lat": 22.4862, "capacity": 9000, "status": "normal"},
    {"name": "佛山三水中转堆场", "code": "GD-FS-001", "yard_type": "yard", "province": "广东", "city": "佛山", "lng": 112.9060, "lat": 23.1867, "capacity": 8000, "status": "normal"},
    {"name": "东莞虎门物流园", "code": "GD-DG-001", "yard_type": "logistics", "province": "广东", "city": "东莞", "lng": 113.6802, "lat": 22.8091, "capacity": 9500, "status": "warning"},
    {"name": "钦州保税堆场", "code": "GX-QZ-001", "yard_type": "yard", "province": "广西", "city": "钦州", "lng": 108.6131, "lat": 21.9589, "capacity": 10000, "status": "warning"},
    {"name": "北海铁山港点位", "code": "GX-BH-001", "yard_type": "logistics", "province": "广西", "city": "北海", "lng": 109.5933, "lat": 21.4930, "capacity": 7600, "status": "normal"},
    {"name": "防城港东湾堆场", "code": "GX-FCG-001", "yard_type": "yard", "province": "广西", "city": "防城港", "lng": 108.3551, "lat": 21.6146, "capacity": 8800, "status": "busy"},
    {"name": "南宁空铁联运点", "code": "GX-NN-001", "yard_type": "logistics", "province": "广西", "city": "南宁", "lng": 108.3669, "lat": 22.8170, "capacity": 7000, "status": "normal"},
]

CARGO_CATEGORIES = ["矿石", "煤炭", "粮食", "机械", "化工", "其他"]


async def upsert_yards() -> dict[str, int]:
    async with SessionLocal() as db:
        code_to_id: dict[str, int] = {}
        for payload in SEED_YARDS:
            stmt = select(Yard).where(Yard.code == payload["code"])
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if existing:
                for key, value in payload.items():
                    setattr(existing, key, value)
                yard = existing
            else:
                yard = Yard(**payload)
                db.add(yard)
            await db.flush()
            code_to_id[yard.code] = yard.id
        await db.commit()
        return code_to_id


async def seed_throughput(code_to_id: dict[str, int]) -> None:
    async with SessionLocal() as db:
        await db.execute(delete(ThroughputDaily))
        today = date.today()
        for yard_code, yard_id in code_to_id.items():
            base = random.randint(220, 480)
            stock = random.randint(2400, 5800)
            for day_offset in range(14):
                stat_date = today - timedelta(days=(13 - day_offset))
                in_teu = base + random.randint(-30, 50)
                out_teu = base + random.randint(-40, 40)
                stock = max(1200, stock + in_teu - out_teu)
                db.add(
                    ThroughputDaily(
                        yard_id=yard_id,
                        stat_date=stat_date,
                        in_teu=in_teu,
                        out_teu=out_teu,
                        stock_teu=stock,
                    )
                )
        await db.commit()


async def seed_cargo(code_to_id: dict[str, int]) -> None:
    async with SessionLocal() as db:
        await db.execute(delete(CargoCategory))
        for yard_id in code_to_id.values():
            for category in CARGO_CATEGORIES:
                db.add(
                    CargoCategory(
                        yard_id=yard_id,
                        category=category,
                        volume=random.randint(200, 1500),
                    )
                )
        await db.commit()


async def seed_alerts(code_to_id: dict[str, int]) -> None:
    async with SessionLocal() as db:
        await db.execute(delete(Alert))
        levels = ["low", "medium", "high"]
        alert_types = ["拥堵", "库存", "设备", "天气", "道路"]
        yard_ids = list(code_to_id.values())
        now = datetime.utcnow()
        for idx in range(36):
            db.add(
                Alert(
                    yard_id=random.choice(yard_ids),
                    level=random.choice(levels),
                    alert_type=random.choice(alert_types),
                    message=f"自动告警#{idx + 1}，请检查堆场作业效率与排队时长",
                    created_at=now - timedelta(minutes=idx * 10),
                )
            )
        await db.commit()


async def seed_vehicles(code_to_id: dict[str, int]) -> None:
    async with SessionLocal() as db:
        await db.execute(delete(Vehicle))
        codes = list(code_to_id.keys())
        for idx in range(60):
            from_code, to_code = random.sample(codes, k=2)
            db.add(
                Vehicle(
                    code=f"VH-{idx + 1:04d}",
                    from_yard_code=from_code,
                    to_yard_code=to_code,
                    progress=round(random.random(), 3),
                    status="running" if idx % 5 else "waiting",
                )
            )
        await db.commit()


async def seed_flow_od() -> None:
    """与 app.services.mock_data.mock_flow() 一致的 OD 边，供 /flow/od 与地图飞线使用。"""
    async with SessionLocal() as db:
        await db.execute(delete(FlowOD))
        for item in mock_flow():
            db.add(
                FlowOD(
                    from_yard_code=item["from_code"],
                    to_yard_code=item["to_code"],
                    value_teu=int(item["value"]),
                )
            )
        await db.commit()


async def main() -> None:
    code_to_id = await upsert_yards()
    await seed_throughput(code_to_id)
    await seed_cargo(code_to_id)
    await seed_alerts(code_to_id)
    await seed_vehicles(code_to_id)
    await seed_flow_od()
    print("Seed completed: Guangdong/Guangxi yards, flow_od, and related datasets inserted.")


if __name__ == "__main__":
    asyncio.run(main())
