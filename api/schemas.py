from typing import Optional

from pydantic import BaseModel, ConfigDict

class SupplierOut(BaseModel):
    """
    Схема ответа API для поставщика. Содержит все поля, возвращаемые клиенту.
    Внешний контракт API.
    """

    id: int
    name: str
    category: str
    region: str
    contacts: Optional[str] = None
    website: Optional[str] = None
    min_order_qty: Optional[str] = None
    price_range: Optional[str] = None
    has_certificates: bool
    delivery_conditions: Optional[str] = None
    notes: Optional[str] = None

    # Позволяет Pydantic автоматически заполнять поля из атрибутов модели SQLAlchemy,
    # чтобы обращаться к полям через 'supplier.name' вместо 'supplier["name"]'.
    model_config = ConfigDict(from_attributes=True)


class ComparisonOut(BaseModel):
    """
    Схема ответа API для сравнения поставщиков. Содержит имя поставщика и краткое резюме.
    Внешний контракт API.
    """
    name: str
    summary: str


class RecommendationOut(BaseModel):
    """
    Схема ответа API для рекомендации. Содержит имя рекомендованного поставщика и обоснование выбора.
    Внешний контракт API.
    """
    name: str
    reason: str


class AIRecommendationOut(BaseModel):
    """
    Схема ответа API для результата рекомендации. Содержит список сравнений поставщиков и готовую рекомендацию.
    Внешний контракт API.
    """
    comparisons: list[ComparisonOut]
    recommendation: RecommendationOut


class SupplierSearchResponse(BaseModel):
    """
    Схема ответа API для поиска поставщиков. Содержит список найденных поставщиков и, при наличии, рекомендации от AI.
    Внешний контракт API.
    """
    suppliers: list[SupplierOut]
    ai_recommendation: Optional[AIRecommendationOut] = None


class FiltersOut(BaseModel):
    """Схема ответа API для фильтров. Содержит уникальные категории и регионы поставщиков."""
    categories: list[str]
    regions: list[str]