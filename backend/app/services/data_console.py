"""Postgres 数据管理台：查询、增删改、CSV 导入（内部工具，生产请自行加鉴权）。"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.cargo import CargoCategory
from app.models.flow_od import FlowOD
from app.models.throughput import ThroughputDaily
from app.models.vehicle import Vehicle
from app.models.yard import Yard
from app.schemas.data_console import (
    AlertCreate,
    AlertUpdate,
    CargoCreate,
    CargoUpdate,
    FlowODCreate,
    FlowODUpdate,
    ImportResult,
    ThroughputCreate,
    ThroughputUpdate,
    VehicleCreate,
    VehicleUpdate,
    YardCreate,
    YardUpdate,
)


# —— Yards ——


async def console_yards_list(db: AsyncSession, skip: int, limit: int) -> tuple[list[Yard], int]:
    total = (await db.execute(select(func.count(Yard.id)))).scalar() or 0
    rows = (
        (await db.execute(select(Yard).order_by(Yard.id).offset(skip).limit(limit))).scalars().all()
    )
    return list(rows), int(total)


async def console_yard_get(db: AsyncSession, yard_id: int) -> Yard | None:
    return await db.get(Yard, yard_id)


async def console_yard_create(db: AsyncSession, body: YardCreate) -> Yard:
    yard = Yard(
        name=body.name,
        code=body.code,
        yard_type=body.yard_type,
        province=body.province,
        city=body.city,
        lng=body.lng,
        lat=body.lat,
        capacity=body.capacity,
        status=body.status,
    )
    db.add(yard)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(yard)
    return yard


async def console_yard_update(db: AsyncSession, yard_id: int, body: YardUpdate) -> Yard | None:
    yard = await db.get(Yard, yard_id)
    if not yard:
        return None
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(yard, k, v)
    await db.commit()
    await db.refresh(yard)
    return yard


async def console_yard_delete(db: AsyncSession, yard_id: int) -> bool:
    yard = await db.get(Yard, yard_id)
    if not yard:
        return False
    await db.execute(delete(ThroughputDaily).where(ThroughputDaily.yard_id == yard_id))
    await db.execute(delete(CargoCategory).where(CargoCategory.yard_id == yard_id))
    await db.execute(delete(Alert).where(Alert.yard_id == yard_id))
    await db.delete(yard)
    await db.commit()
    return True


async def import_yards_csv(db: AsyncSession, raw: bytes) -> ImportResult:
    result = ImportResult()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=2):
        try:
            norm = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            code = norm.get("code") or norm.get("堆场编码")
            if not code:
                result.errors.append({"row": idx, "error": "缺少 code"})
                continue
            body = YardCreate(
                name=norm.get("name") or norm.get("名称") or "",
                code=code,
                yard_type=norm.get("yard_type") or norm.get("类型") or "yard",
                province=norm.get("province") or norm.get("省份") or "",
                city=norm.get("city") or norm.get("城市") or "",
                lng=float(norm.get("lng") or norm.get("经度") or 0),
                lat=float(norm.get("lat") or norm.get("纬度") or 0),
                capacity=int(norm.get("capacity") or norm.get("容量") or 0),
                status=norm.get("status") or norm.get("状态") or "normal",
            )
            existing = (
                await db.execute(select(Yard).where(Yard.code == body.code))
            ).scalar_one_or_none()
            if existing:
                await db.execute(
                    update(Yard)
                    .where(Yard.id == existing.id)
                    .values(
                        name=body.name,
                        yard_type=body.yard_type,
                        province=body.province,
                        city=body.city,
                        lng=body.lng,
                        lat=body.lat,
                        capacity=body.capacity,
                        status=body.status,
                    )
                )
                result.updated += 1
            else:
                db.add(
                    Yard(
                        name=body.name,
                        code=body.code,
                        yard_type=body.yard_type,
                        province=body.province,
                        city=body.city,
                        lng=body.lng,
                        lat=body.lat,
                        capacity=body.capacity,
                        status=body.status,
                    )
                )
                result.inserted += 1
            await db.commit()
        except Exception as e:  # noqa: BLE001
            await db.rollback()
            result.errors.append({"row": idx, "error": str(e)})
    return result


# —— Flow OD ——


async def console_flow_od_list(db: AsyncSession, skip: int, limit: int) -> tuple[list[FlowOD], int]:
    total = (await db.execute(select(func.count(FlowOD.id)))).scalar() or 0
    rows = (
        (await db.execute(select(FlowOD).order_by(FlowOD.id).offset(skip).limit(limit)))
        .scalars()
        .all()
    )
    return list(rows), int(total)


async def console_flow_od_create(db: AsyncSession, body: FlowODCreate) -> FlowOD:
    row = FlowOD(
        from_yard_code=body.from_yard_code,
        to_yard_code=body.to_yard_code,
        value_teu=body.value_teu,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def console_flow_od_update(db: AsyncSession, row_id: int, body: FlowODUpdate) -> FlowOD | None:
    row = await db.get(FlowOD, row_id)
    if not row:
        return None
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(row)
    return row


async def console_flow_od_delete(db: AsyncSession, row_id: int) -> bool:
    row = await db.get(FlowOD, row_id)
    if not row:
        return False
    await db.delete(row)
    await db.commit()
    return True


async def import_flow_od_csv(db: AsyncSession, raw: bytes) -> ImportResult:
    result = ImportResult()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=2):
        try:
            norm = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            fc = norm.get("from_yard_code") or norm.get("from_code") or norm.get("起点编码")
            tc = norm.get("to_yard_code") or norm.get("to_code") or norm.get("终点编码")
            val = int(norm.get("value_teu") or norm.get("value") or norm.get("流量") or 0)
            if not fc or not tc:
                result.errors.append({"row": idx, "error": "缺少起点/终点编码"})
                continue
            existing = (
                await db.execute(
                    select(FlowOD).where(
                        FlowOD.from_yard_code == fc,
                        FlowOD.to_yard_code == tc,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                existing.value_teu = val
                result.updated += 1
            else:
                db.add(FlowOD(from_yard_code=fc, to_yard_code=tc, value_teu=val))
                result.inserted += 1
            await db.commit()
        except Exception as e:  # noqa: BLE001
            await db.rollback()
            result.errors.append({"row": idx, "error": str(e)})
    return result


# —— Throughput ——


async def console_throughput_list(db: AsyncSession, skip: int, limit: int) -> tuple[list[ThroughputDaily], int]:
    total = (await db.execute(select(func.count(ThroughputDaily.id)))).scalar() or 0
    rows = (
        (
            await db.execute(
                select(ThroughputDaily).order_by(
                    ThroughputDaily.stat_date.desc(), ThroughputDaily.id.desc()
                ).offset(skip).limit(limit)
            )
        )
        .scalars()
        .all()
    )
    return list(rows), int(total)


async def console_throughput_create(db: AsyncSession, body: ThroughputCreate) -> ThroughputDaily:
    row = ThroughputDaily(
        yard_id=body.yard_id,
        stat_date=body.stat_date,
        in_teu=body.in_teu,
        out_teu=body.out_teu,
        stock_teu=body.stock_teu,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def console_throughput_update(
    db: AsyncSession, row_id: int, body: ThroughputUpdate
) -> ThroughputDaily | None:
    row = await db.get(ThroughputDaily, row_id)
    if not row:
        return None
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return row


async def console_throughput_delete(db: AsyncSession, row_id: int) -> bool:
    row = await db.get(ThroughputDaily, row_id)
    if not row:
        return False
    await db.delete(row)
    await db.commit()
    return True


async def import_throughput_csv(db: AsyncSession, raw: bytes) -> ImportResult:
    result = ImportResult()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=2):
        try:
            norm = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            ycode = norm.get("yard_code") or norm.get("堆场编码")
            yid_key = norm.get("yard_id")
            if ycode:
                y = (await db.execute(select(Yard).where(Yard.code == ycode))).scalar_one_or_none()
                if not y:
                    result.errors.append({"row": idx, "error": f"未知堆场编码 {ycode}"})
                    continue
                yard_id = y.id
            elif yid_key:
                yard_id = int(yid_key)
            else:
                result.errors.append({"row": idx, "error": "缺少 yard_code 或 yard_id"})
                continue
            stat_raw = norm.get("stat_date") or norm.get("日期") or ""
            stat_date = date.fromisoformat(stat_raw[:10])
            row_obj = ThroughputDaily(
                yard_id=yard_id,
                stat_date=stat_date,
                in_teu=int(norm.get("in_teu") or norm.get("进") or 0),
                out_teu=int(norm.get("out_teu") or norm.get("出") or 0),
                stock_teu=int(norm.get("stock_teu") or norm.get("库存") or 0),
            )
            db.add(row_obj)
            result.inserted += 1
            await db.commit()
        except Exception as e:  # noqa: BLE001
            await db.rollback()
            result.errors.append({"row": idx, "error": str(e)})
    return result


# —— Cargo ——


async def console_cargo_list(db: AsyncSession, skip: int, limit: int) -> tuple[list[CargoCategory], int]:
    total = (await db.execute(select(func.count(CargoCategory.id)))).scalar() or 0
    rows = (
        (await db.execute(select(CargoCategory).order_by(CargoCategory.id).offset(skip).limit(limit)))
        .scalars()
        .all()
    )
    return list(rows), int(total)


async def console_cargo_create(db: AsyncSession, body: CargoCreate) -> CargoCategory:
    row = CargoCategory(yard_id=body.yard_id, category=body.category, volume=body.volume)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def console_cargo_update(db: AsyncSession, row_id: int, body: CargoUpdate) -> CargoCategory | None:
    row = await db.get(CargoCategory, row_id)
    if not row:
        return None
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return row


async def console_cargo_delete(db: AsyncSession, row_id: int) -> bool:
    row = await db.get(CargoCategory, row_id)
    if not row:
        return False
    await db.delete(row)
    await db.commit()
    return True


async def import_cargo_csv(db: AsyncSession, raw: bytes) -> ImportResult:
    result = ImportResult()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=2):
        try:
            norm = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            ycode = norm.get("yard_code") or norm.get("堆场编码")
            if ycode:
                y = (await db.execute(select(Yard).where(Yard.code == ycode))).scalar_one_or_none()
                if not y:
                    result.errors.append({"row": idx, "error": f"未知堆场编码 {ycode}"})
                    continue
                yard_id = y.id
            else:
                yard_id = int(norm.get("yard_id") or 0)
            cat = norm.get("category") or norm.get("货类") or ""
            vol = int(norm.get("volume") or norm.get("货量") or 0)
            if not yard_id or not cat:
                result.errors.append({"row": idx, "error": "缺少 yard 或 category"})
                continue
            existing = (
                await db.execute(
                    select(CargoCategory).where(
                        CargoCategory.yard_id == yard_id,
                        CargoCategory.category == cat,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                existing.volume = vol
                result.updated += 1
            else:
                db.add(CargoCategory(yard_id=yard_id, category=cat, volume=vol))
                result.inserted += 1
            await db.commit()
        except Exception as e:  # noqa: BLE001
            await db.rollback()
            result.errors.append({"row": idx, "error": str(e)})
    return result


# —— Alerts ——


async def console_alerts_list(db: AsyncSession, skip: int, limit: int) -> tuple[list[Alert], int]:
    total = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    rows = (
        (
            await db.execute(
                select(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit)
            )
        )
        .scalars()
        .all()
    )
    return list(rows), int(total)


async def console_alert_create(db: AsyncSession, body: AlertCreate) -> Alert:
    row = Alert(
        yard_id=body.yard_id,
        level=body.level,
        alert_type=body.alert_type,
        message=body.message,
        created_at=datetime.utcnow(),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def console_alert_update(db: AsyncSession, row_id: int, body: AlertUpdate) -> Alert | None:
    row = await db.get(Alert, row_id)
    if not row:
        return None
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return row


async def console_alert_delete(db: AsyncSession, row_id: int) -> bool:
    row = await db.get(Alert, row_id)
    if not row:
        return False
    await db.delete(row)
    await db.commit()
    return True


async def import_alerts_csv(db: AsyncSession, raw: bytes) -> ImportResult:
    result = ImportResult()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=2):
        try:
            norm = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            ycode = norm.get("yard_code")
            if ycode:
                y = (await db.execute(select(Yard).where(Yard.code == ycode))).scalar_one_or_none()
                if not y:
                    result.errors.append({"row": idx, "error": f"未知堆场编码 {ycode}"})
                    continue
                yard_id = y.id
            else:
                yard_id = int(norm.get("yard_id") or 0)
            ts_raw = norm.get("created_at") or norm.get("时间")
            created = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")) if ts_raw else datetime.utcnow()
            db.add(
                Alert(
                    yard_id=yard_id,
                    level=norm.get("level") or "info",
                    alert_type=norm.get("alert_type") or norm.get("类型") or "其它",
                    message=norm.get("message") or norm.get("内容") or "",
                    created_at=created,
                )
            )
            result.inserted += 1
            await db.commit()
        except Exception as e:  # noqa: BLE001
            await db.rollback()
            result.errors.append({"row": idx, "error": str(e)})
    return result


# —— Vehicles ——


async def console_vehicles_list(db: AsyncSession, skip: int, limit: int) -> tuple[list[Vehicle], int]:
    total = (await db.execute(select(func.count(Vehicle.id)))).scalar() or 0
    rows = (
        (await db.execute(select(Vehicle).order_by(Vehicle.id).offset(skip).limit(limit))).scalars().all()
    )
    return list(rows), int(total)


async def console_vehicle_create(db: AsyncSession, body: VehicleCreate) -> Vehicle:
    row = Vehicle(
        code=body.code,
        from_yard_code=body.from_yard_code,
        to_yard_code=body.to_yard_code,
        progress=body.progress,
        status=body.status,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def console_vehicle_update(db: AsyncSession, row_id: int, body: VehicleUpdate) -> Vehicle | None:
    row = await db.get(Vehicle, row_id)
    if not row:
        return None
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    await db.commit()
    await db.refresh(row)
    return row


async def console_vehicle_delete(db: AsyncSession, row_id: int) -> bool:
    row = await db.get(Vehicle, row_id)
    if not row:
        return False
    await db.delete(row)
    await db.commit()
    return True


async def import_vehicles_csv(db: AsyncSession, raw: bytes) -> ImportResult:
    result = ImportResult()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    for idx, row in enumerate(reader, start=2):
        try:
            norm = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            code = norm.get("code") or norm.get("车牌") or norm.get("编号")
            if not code:
                result.errors.append({"row": idx, "error": "缺少 code"})
                continue
            existing = (await db.execute(select(Vehicle).where(Vehicle.code == code))).scalar_one_or_none()
            payload = dict(
                from_yard_code=norm.get("from_yard_code") or norm.get("起点") or "",
                to_yard_code=norm.get("to_yard_code") or norm.get("终点") or "",
                progress=float(norm.get("progress") or 0),
                status=norm.get("status") or "running",
            )
            if existing:
                for k, v in payload.items():
                    setattr(existing, k, v)
                result.updated += 1
            else:
                db.add(Vehicle(code=code, **payload))
                result.inserted += 1
            await db.commit()
        except Exception as e:  # noqa: BLE001
            await db.rollback()
            result.errors.append({"row": idx, "error": str(e)})
    return result
