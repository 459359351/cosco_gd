"""系统字典：省份、城市、堆场状态、货种等基础配置。"""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sys_dict import SysDict
from app.schemas.sys_dict import DictTypeMeta, SysDictCreate, SysDictUpdate

DICT_TYPES: list[DictTypeMeta] = [
    DictTypeMeta(type="province", label="省份"),
    DictTypeMeta(type="city", label="城市", has_parent=True),
    DictTypeMeta(type="yard_type", label="堆场类型"),
    DictTypeMeta(type="yard_status", label="堆场状态"),
    DictTypeMeta(type="cargo_category", label="货种类别"),
    DictTypeMeta(type="alert_level", label="预警级别"),
    DictTypeMeta(type="alert_type", label="预警类型"),
    DictTypeMeta(type="vehicle_status", label="车辆状态"),
]

DICT_TYPE_SET = {m.type for m in DICT_TYPES}


def dict_type_meta(dict_type: str) -> DictTypeMeta | None:
    for m in DICT_TYPES:
        if m.type == dict_type:
            return m
    return None


async def list_dict(
    db: AsyncSession,
    dict_type: str,
    parent_code: str | None = None,
    enabled_only: bool = True,
) -> list[SysDict]:
    q = select(SysDict).where(SysDict.dict_type == dict_type)
    if parent_code is not None:
        q = q.where(SysDict.parent_code == parent_code)
    if enabled_only:
        q = q.where(SysDict.enabled.is_(True))
    q = q.order_by(SysDict.sort_order, SysDict.id)
    return list((await db.execute(q)).scalars().all())


async def get_dict(db: AsyncSession, row_id: int) -> SysDict | None:
    return await db.get(SysDict, row_id)


async def create_dict(db: AsyncSession, body: SysDictCreate) -> SysDict:
    row = SysDict(
        dict_type=body.dict_type,
        code=body.code,
        label=body.label,
        parent_code=body.parent_code,
        sort_order=body.sort_order,
        enabled=body.enabled,
        remark=body.remark,
    )
    db.add(row)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(row)
    return row


async def update_dict(db: AsyncSession, row_id: int, body: SysDictUpdate) -> SysDict | None:
    row = await db.get(SysDict, row_id)
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


async def delete_dict(db: AsyncSession, row_id: int) -> bool:
    row = await db.get(SysDict, row_id)
    if not row:
        return False
    if row.dict_type == "province":
        await db.execute(delete(SysDict).where(SysDict.dict_type == "city", SysDict.parent_code == row.code))
    await db.delete(row)
    await db.commit()
    return True


async def count_by_type(db: AsyncSession, dict_type: str) -> int:
    return int(
        (await db.execute(select(func.count(SysDict.id)).where(SysDict.dict_type == dict_type))).scalar() or 0
    )
