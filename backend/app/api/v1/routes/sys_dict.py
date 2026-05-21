from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.sys_dict import DictTypeMeta, SysDictCreate, SysDictRowOut, SysDictUpdate
from app.services import sys_dict as svc

router = APIRouter()


@router.get("/types", response_model=list[DictTypeMeta])
async def get_dict_types() -> list[DictTypeMeta]:
    return svc.DICT_TYPES


@router.get("", response_model=dict)
async def list_sys_dict(
    type: str = Query(..., alias="type", description="字典类型"),
    parent: str | None = Query(default=None, description="父级 code，如城市所属省份"),
    enabled_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if type not in svc.DICT_TYPE_SET:
        raise HTTPException(status_code=400, detail=f"unknown dict type: {type}")
    rows = await svc.list_dict(db, type, parent_code=parent, enabled_only=enabled_only)
    return {
        "type": type,
        "items": [SysDictRowOut.model_validate(r).model_dump() for r in rows],
    }


@router.post("", response_model=SysDictRowOut)
async def create_sys_dict(body: SysDictCreate, db: AsyncSession = Depends(get_db)) -> SysDictRowOut:
    if body.dict_type not in svc.DICT_TYPE_SET:
        raise HTTPException(status_code=400, detail=f"unknown dict type: {body.dict_type}")
    meta = svc.dict_type_meta(body.dict_type)
    if meta and meta.has_parent and not body.parent_code:
        raise HTTPException(status_code=400, detail="parent_code is required for this dict type")
    try:
        row = await svc.create_dict(db, body)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="dict code already exists for this type") from None
    return SysDictRowOut.model_validate(row)


@router.patch("/{row_id}", response_model=SysDictRowOut)
async def update_sys_dict(
    row_id: int, body: SysDictUpdate, db: AsyncSession = Depends(get_db)
) -> SysDictRowOut:
    try:
        row = await svc.update_dict(db, row_id, body)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="update conflict") from None
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return SysDictRowOut.model_validate(row)


@router.delete("/{row_id}")
async def delete_sys_dict(row_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await svc.delete_dict(db, row_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}
