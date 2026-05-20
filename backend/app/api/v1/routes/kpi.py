from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard import kpi_overview

router = APIRouter()


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)) -> dict:
    return await kpi_overview(db)
