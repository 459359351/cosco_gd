from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard import cargo_distribution

router = APIRouter()


@router.get("/distribution")
async def get_distribution(db: AsyncSession = Depends(get_db)) -> dict:
    return await cargo_distribution(db)
