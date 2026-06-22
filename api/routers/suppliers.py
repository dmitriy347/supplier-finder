from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import SupplierOut
from database import get_db
from services.suppliers_service import search_suppliers, get_top_candidates

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("/", response_model=list[SupplierOut])
async def get_suppliers(
        category: Optional[str] = None,
        region: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
):
    """Возвращает список отсортированных поставщиков."""
    suppliers = await search_suppliers(db, category=category, region=region)

    return suppliers