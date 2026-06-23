import json
import os
from typing import Optional

from dotenv import load_dotenv
from groq import AsyncGroq
from pydantic import BaseModel

from models.supplier import Supplier

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


class ComparisonItem(BaseModel):
    """
    Pydantic-модель для сравнения поставщиков, содержит имя поставщика и краткое резюме.
    Внутренний слой парсинга.
    """
    name: str
    summary: str


class Recommendation(BaseModel):
    """
    Pydantic-модель для рекомендации, содержит имя рекомендованного поставщика и обоснование выбора.
    Рекомендация строится на основе анализа модели.
    Внутренний слой парсинга.
    """
    name: str
    reason: str


class AIRecommendationResult(BaseModel):
    """
    Pydantic-модель для результата рекомендации, содержит список сравнений поставщиков и готовую рекомендацию.
    Внутренний слой парсинга.
    """
    comparisons: list[ComparisonItem]
    recommendation: Recommendation


def _supplier_to_dict(supplier: Supplier) -> dict:
    """
    Преобразует объект Supplier в словарь для передачи в промпт.
    Передаем в промпт только ключевые поля, влияющие на решение.
    """
    return {
        "name": supplier.name,
        "min_order_qty": supplier.min_order_qty,
        "price_range": supplier.price_range,
        "has_certificates": supplier.has_certificates,
        "delivery_conditions": supplier.delivery_conditions,
        "notes": supplier.notes
    }


def _build_prompt(suppliers_data: list[dict]) -> str:
    """Построение промпта для модели на основе данных поставщиков."""
    return f"""Ты помогаешь закупщику ресторана выбрать поставщика.
    Ниже список кандидатов в формате JSON. Используй ТОЛЬКО данные из этого
    списка – не добавляй факты, которых там нет.
    
    {json.dumps(suppliers_data, ensure_ascii=False, indent=2)}
    
    Верни ответ СТРОГО в формате JSON, без markdown-обёртки (без ```),
    без преамбулы и пояснений до или после JSON:
    {{
      "comparisons": [
        {{"name": "...", "summary": "1-2 предложения"}}
      ],
      "recommendation": {{
        "name": "...",
        "reason": "почему именно этот, со ссылкой на цену/MOQ/сертификаты/доставку"
      }}
    }}"""


def _strip_markdown_wrapper(text: str) -> str:
    """Если модель обернула JSON-ответ в markdown-блок, извлекаем только JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


async def get_ai_recommendation(suppliers: list[Supplier]) -> Optional[AIRecommendationResult]:
    """
    Ожидает отобранный топ-N поставщиков (см. get_top_candidates).
    При любой ошибке возвращает None (невалидный JSON, сбой сети, недоступность GROQ).
    """
    # Если поставщиков меньше 2, то сравнивать нечего - возвращаем None.
    if len(suppliers) < 2:
        return None

    # Преобразуем список моделей Supplier в список словарей для передачи в промпт.
    suppliers_data = [_supplier_to_dict(s) for s in suppliers]
    prompt = _build_prompt(suppliers_data)

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        # Извлекаем сырой текстовый ответ модели.
        raw_text = response.choices[0].message.content
        # Очищаем от возможной markdown-обёртки.
        cleaned_text = _strip_markdown_wrapper(raw_text)
        # Распарсим строку JSON в словарь Python.
        parsed_text = json.loads(cleaned_text)
        return AIRecommendationResult(**parsed_text)

    except Exception:
        return None