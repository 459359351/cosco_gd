"""驾驶舱 Postgres 数据管理 API（开发用，生产请加鉴权与审计）。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.data_console import (
    AlertCreate,
    AlertRowOut,
    AlertUpdate,
    CargoCreate,
    CargoRowOut,
    CargoUpdate,
    FlowODCreate,
    FlowODRowOut,
    FlowODUpdate,
    ImportResult,
    ThroughputCreate,
    ThroughputRowOut,
    ThroughputUpdate,
    VehicleCreate,
    VehicleRowOut,
    VehicleUpdate,
    YardCreate,
    YardRowOut,
    YardUpdate,
)
from app.services import data_console as svc

router = APIRouter()


# —— Yards ——


@router.get("/yards", response_model=dict)
async def list_yards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rows, total = await svc.console_yards_list(db, skip, limit)
    return {"total": total, "items": [YardRowOut.model_validate(r).model_dump() for r in rows]}


@router.post("/yards", response_model=YardRowOut)
async def create_yard(body: YardCreate, db: AsyncSession = Depends(get_db)) -> YardRowOut:
    try:
        row = await svc.console_yard_create(db, body)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="code 已存在") from None
    return YardRowOut.model_validate(row)


@router.patch("/yards/{yard_id}", response_model=YardRowOut)
async def update_yard(
    yard_id: int, body: YardUpdate, db: AsyncSession = Depends(get_db)
) -> YardRowOut:
    row = await svc.console_yard_update(db, yard_id, body)
    if not row:
        raise HTTPException(status_code=404, detail="yard not found")
    return YardRowOut.model_validate(row)


@router.delete("/yards/{yard_id}")
async def delete_yard(yard_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await svc.console_yard_delete(db, yard_id)
    if not ok:
        raise HTTPException(status_code=404, detail="yard not found")
    return {"ok": True}


@router.post("/yards/import", response_model=ImportResult)
async def import_yards(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> ImportResult:
    raw = await file.read()
    return await svc.import_yards_csv(db, raw)


# —— Flow OD ——


@router.get("/flow-od", response_model=dict)
async def list_flow_od(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rows, total = await svc.console_flow_od_list(db, skip, limit)
    return {"total": total, "items": [FlowODRowOut.model_validate(r).model_dump() for r in rows]}


@router.post("/flow-od", response_model=FlowODRowOut)
async def create_flow_od(body: FlowODCreate, db: AsyncSession = Depends(get_db)) -> FlowODRowOut:
    try:
        row = await svc.console_flow_od_create(db, body)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="该 OD 边已存在") from None
    return FlowODRowOut.model_validate(row)


@router.patch("/flow-od/{row_id}", response_model=FlowODRowOut)
async def update_flow_od(
    row_id: int, body: FlowODUpdate, db: AsyncSession = Depends(get_db)
) -> FlowODRowOut:
    try:
        row = await svc.console_flow_od_update(db, row_id, body)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="唯一约束冲突") from None
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return FlowODRowOut.model_validate(row)


@router.delete("/flow-od/{row_id}")
async def delete_flow_od(row_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await svc.console_flow_od_delete(db, row_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.post("/flow-od/import", response_model=ImportResult)
async def import_flow_od(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> ImportResult:
    raw = await file.read()
    return await svc.import_flow_od_csv(db, raw)


# —— Throughput ——


@router.get("/throughput", response_model=dict)
async def list_throughput(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rows, total = await svc.console_throughput_list(db, skip, limit)
    return {"total": total, "items": [ThroughputRowOut.model_validate(r).model_dump() for r in rows]}


@router.post("/throughput", response_model=ThroughputRowOut)
async def create_throughput(
    body: ThroughputCreate, db: AsyncSession = Depends(get_db)
) -> ThroughputRowOut:
    row = await svc.console_throughput_create(db, body)
    return ThroughputRowOut.model_validate(row)


@router.patch("/throughput/{row_id}", response_model=ThroughputRowOut)
async def update_throughput(
    row_id: int, body: ThroughputUpdate, db: AsyncSession = Depends(get_db)
) -> ThroughputRowOut:
    row = await svc.console_throughput_update(db, row_id, body)
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return ThroughputRowOut.model_validate(row)


@router.delete("/throughput/{row_id}")
async def delete_throughput(row_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await svc.console_throughput_delete(db, row_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.post("/throughput/import", response_model=ImportResult)
async def import_throughput(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> ImportResult:
    raw = await file.read()
    return await svc.import_throughput_csv(db, raw)


# —— Cargo ——


@router.get("/cargo", response_model=dict)
async def list_cargo(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rows, total = await svc.console_cargo_list(db, skip, limit)
    return {"total": total, "items": [CargoRowOut.model_validate(r).model_dump() for r in rows]}


@router.post("/cargo", response_model=CargoRowOut)
async def create_cargo(body: CargoCreate, db: AsyncSession = Depends(get_db)) -> CargoRowOut:
    row = await svc.console_cargo_create(db, body)
    return CargoRowOut.model_validate(row)


@router.patch("/cargo/{row_id}", response_model=CargoRowOut)
async def update_cargo(row_id: int, body: CargoUpdate, db: AsyncSession = Depends(get_db)) -> CargoRowOut:
    row = await svc.console_cargo_update(db, row_id, body)
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return CargoRowOut.model_validate(row)


@router.delete("/cargo/{row_id}")
async def delete_cargo(row_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await svc.console_cargo_delete(db, row_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.post("/cargo/import", response_model=ImportResult)
async def import_cargo(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> ImportResult:
    raw = await file.read()
    return await svc.import_cargo_csv(db, raw)


# —— Alerts ——


@router.get("/alerts", response_model=dict)
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rows, total = await svc.console_alerts_list(db, skip, limit)
    return {"total": total, "items": [AlertRowOut.model_validate(r).model_dump() for r in rows]}


@router.post("/alerts", response_model=AlertRowOut)
async def create_alert(body: AlertCreate, db: AsyncSession = Depends(get_db)) -> AlertRowOut:
    row = await svc.console_alert_create(db, body)
    return AlertRowOut.model_validate(row)


@router.patch("/alerts/{row_id}", response_model=AlertRowOut)
async def update_alert(row_id: int, body: AlertUpdate, db: AsyncSession = Depends(get_db)) -> AlertRowOut:
    row = await svc.console_alert_update(db, row_id, body)
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return AlertRowOut.model_validate(row)


@router.delete("/alerts/{row_id}")
async def delete_alert(row_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await svc.console_alert_delete(db, row_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.post("/alerts/import", response_model=ImportResult)
async def import_alerts(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> ImportResult:
    raw = await file.read()
    return await svc.import_alerts_csv(db, raw)


# —— Vehicles ——


@router.get("/vehicles", response_model=dict)
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> dict:
    rows, total = await svc.console_vehicles_list(db, skip, limit)
    return {"total": total, "items": [VehicleRowOut.model_validate(r).model_dump() for r in rows]}


@router.post("/vehicles", response_model=VehicleRowOut)
async def create_vehicle(body: VehicleCreate, db: AsyncSession = Depends(get_db)) -> VehicleRowOut:
    try:
        row = await svc.console_vehicle_create(db, body)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="code 已存在") from None
    return VehicleRowOut.model_validate(row)


@router.patch("/vehicles/{row_id}", response_model=VehicleRowOut)
async def update_vehicle(row_id: int, body: VehicleUpdate, db: AsyncSession = Depends(get_db)) -> VehicleRowOut:
    row = await svc.console_vehicle_update(db, row_id, body)
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return VehicleRowOut.model_validate(row)


@router.delete("/vehicles/{row_id}")
async def delete_vehicle(row_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await svc.console_vehicle_delete(db, row_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.post("/vehicles/import", response_model=ImportResult)
async def import_vehicles(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> ImportResult:
    raw = await file.read()
    return await svc.import_vehicles_csv(db, raw)


@router.get("/import-help")
async def import_help() -> dict:
    """CSV 列说明（UTF-8，建议带表头；Excel 可另存为 CSV）。"""
    return {
        "yards": "name,code,yard_type,province,city,lng,lat,capacity,status（或中文表头：名称,堆场编码,...）",
        "flow_od": "from_yard_code,to_yard_code,value_teu",
        "throughput": "yard_code,stat_date,in_teu,out_teu,stock_teu（或 yard_id）",
        "cargo": "yard_code,category,volume",
        "alerts": "yard_id 或 yard_code, level, alert_type, message, created_at(可选 ISO)",
        "vehicles": "code,from_yard_code,to_yard_code,progress,status",
    }
