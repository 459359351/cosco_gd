from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard import throughput_trend

router = APIRouter()


@router.get("/trend")
async def get_trend(
    range: str = Query(default="7d", pattern=r"^\d+d$"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    days = int(range.replace("d", ""))
    return await throughput_trend(db, days=days)
