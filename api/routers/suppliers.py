from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import SupplierSearchResponse
from database import get_db
from services.ai_recommender import get_ai_recommendation
from services.suppliers_service import search_suppliers, get_top_candidates

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("/", response_model=SupplierSearchResponse)
async def get_suppliers(
        category: Optional[str] = None,
        region: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
):
    """
    Эндпоинт для поиска поставщиков по категории и региону.
    Возвращает список найденных поставщиков и, при наличии, рекомендации от AI.
    """
    suppliers = await search_suppliers(db, category=category, region=region)
    top_candidates = get_top_candidates(suppliers)
    ai_result = await get_ai_recommendation(top_candidates)

    return {
        "suppliers": suppliers,
        "ai_recommendation": ai_result.model_dump() if ai_result else None,
    }
