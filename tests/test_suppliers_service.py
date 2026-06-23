from dataclasses import dataclass
from typing import Optional

from services.suppliers_service import _extract_min_price, _sort_key, get_top_candidates


@dataclass
class FakeSupplier:
    name: str
    price_range: Optional[str]
    has_certificates: bool


# --- _extract_min_price ---

def test_extract_min_price_standard():
    assert _extract_min_price("300-380 ₽/кг") == 300.0

def test_extract_min_price_none():
    assert _extract_min_price(None) == float("inf")

def test_extract_min_price_no_digits():
    assert _extract_min_price("по договорённости") == float("inf")


# --- _sort_key ---

def test_sort_key_certified_first():
    """Сертификат важнее цены - сертифицированный должен идти раньше."""
    certified = FakeSupplier("А", "500-600 ₽/кг", has_certificates=True)
    no_cert = FakeSupplier("Б", "200-300 ₽/кг", has_certificates=False)
    assert _sort_key(certified) < _sort_key(no_cert)

def test_sort_key_same_cert_by_price():
    """При наличии сертификата - дешевый идёт первым."""
    cheaper = FakeSupplier("А", "280-340 ₽/кг", has_certificates=True)
    pricier = FakeSupplier("Б", "350-420 ₽/кг", has_certificates=True)
    assert _sort_key(cheaper) < _sort_key(pricier)

def test_sort_key_same_cert_same_price_by_name():
    """При одинаковой цене и сертификате - сортировка по имени."""
    a = FakeSupplier("А", "300-400 ₽/кг", has_certificates=True)
    b = FakeSupplier("Б", "300-400 ₽/кг", has_certificates=True)
    assert _sort_key(a) < _sort_key(b)


# --- get_top_candidates ---

def make_list(n: int) -> list[FakeSupplier]:
    return [FakeSupplier(f"Поставщик {i}", f"{300 + i * 10}-400 ₽/кг", True) for i in range(n)]

def test_top_candidates_returns_5_from_7():
    """Проверяем, что из 7 поставщиков возвращается только 5."""
    assert len(get_top_candidates(make_list(7))) == 5

def test_top_candidates_returns_all_if_less_than_limit():
    """Проверяем, что если поставщиков меньше limit (5), то возвращаются все."""
    suppliers = make_list(3)
    assert get_top_candidates(suppliers) == suppliers