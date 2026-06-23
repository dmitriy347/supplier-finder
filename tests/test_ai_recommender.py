import pytest
from dataclasses import dataclass
from typing import Optional

from services.ai_recommender import _strip_markdown_wrapper, get_ai_recommendation


@dataclass
class FakeSupplier:
    name: str
    price_range: Optional[str]
    has_certificates: bool
    min_order_qty: Optional[str] = None
    delivery_conditions: Optional[str] = None
    notes: Optional[str] = None


# --- _strip_markdown_wrapper ---

def test_strip_plain_json_unchanged():
    """Чистый JSON без обёртки - возвращается как есть."""
    json_str = '{"key": "value"}'
    assert _strip_markdown_wrapper(json_str) == json_str

def test_strip_markdown_json_block():
    """JSON в ```json ... ``` — извлекается только JSON."""
    wrapped = '```json\n{"key": "value"}\n```'
    assert _strip_markdown_wrapper(wrapped) == '{"key": "value"}'


# --- get_ai_recommendation: кейс без вызова Groq ---

@pytest.mark.asyncio
async def test_get_ai_recommendation_single_supplier_returns_none():
    """Меньше 2 поставщиков - None, до Groq не доходит."""
    supplier = FakeSupplier("АгроСнаб", "300-400 ₽/кг", has_certificates=True)
    result = await get_ai_recommendation([supplier])
    assert result is None

@pytest.mark.asyncio
async def test_get_ai_recommendation_empty_list_returns_none():
    """Пустой список - None."""
    result = await get_ai_recommendation([])
    assert result is None