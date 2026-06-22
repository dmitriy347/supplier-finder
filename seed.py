import asyncio
import json
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, async_session, Base
from models.supplier import Supplier

SEED_FILE = Path(__file__).parent / "data" / "seed_suppliers.json"

def load_seed_data() -> list[dict]:
    """Читает данные из файла и возвращает их в виде списка словарей."""
    with open(SEED_FILE, encoding="utf-8") as f:
        return json.load(f)

async def seed_suppliers(session: AsyncSession, suppliers_data: list[dict]) -> int:
    """
    Очищает таблицу suppliers и заполняет её данными.
    Не открывает и не коммитит сессию.
    """
    await session.execute(delete(Supplier))
    for item in suppliers_data:
        session.add(Supplier(**item))
    await session.commit()
    return len(suppliers_data)

async def main():
    # создаём таблицы, если их ещё нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # читаем данные из файла
    suppliers_data = load_seed_data()

    # загружаем данные в БД
    async with async_session() as session:
        count = await seed_suppliers(session, suppliers_data)

    print(f"Загружено {count} поставщиков (таблица предварительно очищена)")

if __name__ == "__main__":
    asyncio.run(main())