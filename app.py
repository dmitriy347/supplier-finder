import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Supplier Finder", page_icon="🔍", layout="centered")
st.title("Сервис для поиска поставщиков продуктов питания")
st.caption("Находите и сравнивайте поставщиков продуктов питания по категории и региону")


@st.cache_data(ttl=60)
def fetch_filters() -> dict:
    """
    Возвращает уникальные значения категорий и регионов из backend API.
    Кэшируется на 60 секунд.
    Таймаут увеличен под "холодный старт" backend на Render free tier (просыпание после простоя занимает 50 секунд).
    """
    response = requests.get(f"{API_URL}/api/suppliers/filters", timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_suppliers(category: str, region: str) -> dict:
    """Возвращает по заданным фильтрам список поставщиков и рекомендации от AI."""
    response = requests.get(
        f"{API_URL}/api/suppliers/",
        params={"category": category, "region": region},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


try:
    with st.spinner("Подключаемся к серверу… при первом обращении это может занять до минуты"):
        filters = fetch_filters()
except requests.RequestException:
    st.error("Не удалось подключиться к backend. Убедитесь, что сервер запущен (`uvicorn api.main:app`).")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    category = st.selectbox(
        "Категория",
        filters["categories"],
        index=None,
        placeholder="Выберите категорию",
    )
with col2:
    region = st.selectbox(
        "Регион",
        filters["regions"],
        index=None,
        placeholder="Выберите регион",
    )

if st.button("Найти", type="primary"):
    if not category or not region:
        st.warning("Пожалуйста, выберите категорию и регион.")
        st.stop()

    try:
        data = fetch_suppliers(category, region)
    except requests.RequestException:
        st.error("Ошибка при обращении к backend. Попробуйте ещё раз.")
        st.stop()

    suppliers = data["suppliers"]
    ai_recommendation = data["ai_recommendation"]

    if not suppliers:
        st.info("По заданным фильтрам поставщики не найдены.")
        st.stop()

    if ai_recommendation:
        st.subheader("AI-Рекомендация")
        rec = ai_recommendation["recommendation"]
        st.success(f"**{rec['name']}**\n\n{rec['reason']}")

        with st.expander("Сравнение кандидатов"):
            for item in ai_recommendation["comparisons"]:
                st.markdown(f"**{item['name']}** — {item['summary']}")

    st.subheader(f"Найдено поставщиков: {len(suppliers)}")

    for supplier in suppliers:
        with st.container(border=True):
            st.markdown(f"### {supplier['name']}")
            cert_label = "✅ Есть сертификаты" if supplier["has_certificates"] else "⚠️ Нет сертификатов"
            st.caption(cert_label)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Цена:** {supplier['price_range'] or '—'}")
                st.markdown(f"**Доставка:** {supplier['delivery_conditions'] or '—'}")
                st.markdown(f"**MOQ:** {supplier['min_order_qty'] or '—'}")

            with c2:
                st.markdown(f"**Контакты:** {supplier['contacts'] or '—'}")
                st.markdown(f"**Сайт:** {supplier['website'] or '—'}")

            if supplier["notes"]:
                st.caption(f'Заметки по поставщику: {supplier["notes"]}')