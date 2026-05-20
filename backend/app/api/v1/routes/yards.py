from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard import list_yards, yard_detail

router = APIRouter()


@router.get("")
async def get_yards(
    province: str | None = Query(default=None, description="按省份筛选"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    yards = await list_yards(db, province=province)
    features = [
        {
            "type": "Feature",
            "properties": item,
            "geometry": {"type": "Point", "coordinates": [item["lng"], item["lat"]]},
        }
        for item in yards
    ]
    return {"items": yards, "geojson": {"type": "FeatureCollection", "features": features}}


@router.get("/{yard_id}/detail")
async def get_yard_detail(yard_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    detail = await yard_detail(db, yard_id)
    if not detail:
        raise HTTPException(status_code=404, detail="yard not found")
    return detail
