# Supplier Finder

> Сервис для поиска поставщиков продуктов питания. Помогает закупщику ресторана быстро найти и сравнить поставщиков, и **принять решение**, с кем связаться первым и почему.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-000000?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Groq](https://img.shields.io/badge/Groq-000000?logo=groq&logoColor=white)](https://www.groq.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![pytest](https://img.shields.io/badge/pytest-000000?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

## Демо

- **Frontend (Streamlit Community Cloud):** https://supplier-finder-t.streamlit.app/
- **Backend API (Render):** https://supplier-finder-yqqn.onrender.com/docs _(free-тариф, при первом обращении после простоя backend может "просыпаться" до минуты)_

## Зачем это нужно

Закупщик ресторана или сети тратит время на сравнение поставщиков: у кого цена ниже / есть сертификаты / быстрее доставка. Обычно это сведение данных в голове или в Excel.

Сервис закрывает именно этот момент: после поиска по категории и региону AI анализирует найденных поставщиков (цена, MOQ, наличие сертификата, условия доставки) и формирует короткую рекомендацию – **с кого начать**, и почему. Это не чат-бот, а ИИ, встроенный в конкретный шаг бизнес-процесса — закуп.

## Архитектура

```
Streamlit UI  ──HTTP──▶  FastAPI backend  ──▶  SQLite (suppliers)
                              │
                              ▼
                      AI Recommender Service
       (Groq API: сравнение топ-N кандидатов → рекомендация)
```

Поток данных:
1. Пользователь выбирает категорию товара и регион в Streamlit-интерфейсе.
2. Backend возвращает отфильтрованный и отсортированный список поставщиков из БД (сначала с сертификатами, затем по возрастанию цены, затем по названию).
3. Если поставщиков > 1 — топ-N отправляются в AI Recommender, который возвращает сравнение по каждому и рекомендацию в строгом JSON-формате.
4. Streamlit-интерфейс отображает карточки поставщиков и блок с AI-рекомендацией.

## Стек и почему именно так

| Слой | Технология | Почему                                                                                                         |
|---|---|----------------------------------------------------------------------------------------------------------------|
| Backend | FastAPI | Async из коробки, удобная работа с REST API                                                                    |
| БД | SQLite + SQLAlchemy (async) + aiosqlite | Для прототипа не нужен отдельный сервис БД                                                                     |                                                                                                              
| Frontend | Streamlit | Для экономии рабочего времени по сравнению с отдельной вёрсткой. Уместен для быстрых внутренних AI-инструментов |
| AI | Groq API (`llama-3.3-70b-versatile`) | Быстрый и бесплатный для прототипа, модель задаётся через `GROQ_MODEL`                     |

## Почему без Alembic

Миграции (Alembic) в этом проекте осознанно не используются. Схема БД фиксирована на момент прототипа, таблица создаётся один раз через `Base.metadata.create_all` в `seed.py`, и для MVP нет практической пользы вводить миграционный слой.

## Данные

`data/seed_suppliers.json` — тестовый набор данных: 47 поставщиков, 4 категории (ингредиенты, готовая продукция, упаковка, напитки), 3 региона (Москва, Санкт-Петербург, Казань). Данные реалистичны по структуре, но не являются результатом живого скрейпинга (сознательное решение).

В реальном сценарии данные могли бы собираться из открытых B2B-каталогов.

## Структура проекта

```
supplier-finder/
├── app.py                      # Streamlit-приложение (UI)
├── api/
│   ├── main.py
│   ├── schemas.py               # Pydantic-схемы — внешний контракт API
│   └── routers/
│       └── suppliers.py
│
├── services/                    # Бизнес-логика
│   ├── ai_recommender.py        # Сравнение и рекомендация (Groq)
│   └── suppliers_service.py     # Поиск, фильтрация, сортировка
│
├── models/                      # SQLAlchemy-модели
│   └── supplier.py
│
├── data/
│   └── seed_suppliers.json      # Тестовый датасет
│
├── tests/
│   ├── test_ai_recommender.py
│   └── test_suppliers_service.py
│
├── seed.py                      # Заполнение БД из файла
├── database.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Запуск локально (Docker)

```bash
cp .env.example .env
```

Заполните `.env`:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
API_URL=http://api:8000
```

Запуск:

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000`, Swagger: `http://localhost:8000/docs`
- Streamlit UI: `http://localhost:8501`

База заполняется автоматически при старте контейнера `api` (`seed.py` отрабатывает перед `uvicorn`).

## API

### `GET /api/suppliers/`

Поиск поставщиков по фильтрам.

| Параметр | Тип | Описание |
|---|---|---|
| `category` | str, опционально | Категория товара |
| `region` | str, опционально | Регион |

Возвращает список поставщиков, и AI-рекомендацию (если поставщиков >1).

### `GET /api/suppliers/filters`

Возвращает доступные значения `category` и `region` для построения фильтров в UI.

## Тесты

```bash
pip install -r requirements.txt
pytest
```

Покрыты:
- сортировка и отбор топ-N (`test_suppliers_service.py`);
- разбор ответа модели и обработка ошибок AI-рекомендации (`test_ai_recommender.py`).

## Путь миграции на PostgreSQL

Если проект пойдёт дальше прототипа:
1. Добавить сервис `db` (образ `postgres`) в `docker-compose.yml`.
2. Сменить `DATABASE_URL` в `.env` на `postgresql+asyncpg://...`.
3. Добавить `asyncpg` в зависимости.
4. Код моделей и сервисов не меняется.