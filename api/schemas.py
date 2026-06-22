from typing import Optional

from pydantic import BaseModel, ConfigDict

class SupplierOut(BaseModel):
    """Схема ответа API для поставщика. Содержит все поля, возвращаемые клиенту."""

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

