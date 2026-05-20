from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard import od_flow

router = APIRouter()


@router.get("/od")
async def get_od(db: AsyncSession = Depends(get_db)) -> dict:
    return await od_flow(db)
