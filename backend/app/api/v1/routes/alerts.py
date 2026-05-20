from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard import recent_alerts

router = APIRouter()


@router.get("/recent")
async def get_recent_alerts(db: AsyncSession = Depends(get_db)) -> dict:
    return await recent_alerts(db)
