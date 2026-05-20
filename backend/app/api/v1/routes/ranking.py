from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard import ranking_yards

router = APIRouter()


@router.get("/yards")
async def get_ranking(
    metric: str = Query(default="teu"),
    top: int = Query(default=10, ge=1, le=20),
    province: str | None = Query(default=None, description="与 /yards 一致，按省筛排行"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return {"metric": metric, **(await ranking_yards(db, top=top, province=province))}
