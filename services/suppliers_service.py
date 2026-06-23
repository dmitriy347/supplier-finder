import re
from typing import Optional

from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from models.supplier import Supplier


def _extract_min_price(price_range: Optional[str]) -> float:
    """
    Извлекает нижнюю границу цены из строки вида '300-380 ₽/кг'.
    Если не удалось распарсить - возвращает inf (бесконечность),
    чтобы такой поставщик не ломал логику и попал в конец списка для сортировки.
    """
    if not price_range:
        return float("inf")
    # Ищем первое число в строке, которое будет нижней границей ценового диапазона.
    match = re.search(r"(\d+)", price_range)
    return float(match.group() if match else float("inf"))


def _sort_key(supplier: Supplier) -> tuple:
    """
    Сортировка: сначала по наличию сертификата, затем по возрастанию цены,
    затем по имени (при равенстве первых двух критериев).
    'not has_certificates' - превращает True в 0 (есть сертификат), а False в 1 (нет сертификата),
    чтобы при сортировке сертифицированные поставщики были первыми.
    """
    return (not supplier.has_certificates, _extract_min_price(supplier.price_range), supplier.name)


async def search_suppliers(
        session: AsyncSession,
        category: Optional[str] = None,
        region: Optional[str] = None
) -> list[Supplier]:
    """
    Возвращает поставщиков по фильтрам категория/регион. Показывается пользователю полностью.
    Поставщики отсортированы по правилу: наличие сертификата -> цена по возрастанию.
    """
    query = select(Supplier)
    if category:
        query = query.where(Supplier.category == category)
    if region:
        query = query.where(Supplier.region == region)

    result = await session.execute(query)
    suppliers = list(result.scalars().all())

    return sorted(suppliers, key=_sort_key)


def get_top_candidates(suppliers: list[Supplier], limit: int = 5) -> list[Supplier]:
    """
    Возвращает топ-N из ранее отсортированного списка. Попадает в AI-блок.
    Если поставщиков <5, возвращает всех.
    """
    return suppliers[:limit]


async def get_available_filters(session: AsyncSession) -> dict:
    """Возвращает уникальные значения category и region из БД."""
    categories_result = await session.execute(
        select(distinct(Supplier.category)).order_by(Supplier.category)
    )
    regions_result = await session.execute(
        select(distinct(Supplier.region)).order_by(Supplier.region)
    )
    return {
        "categories": list(categories_result.scalars().all()),
        "regions": list(regions_result.scalars().all()),
    }