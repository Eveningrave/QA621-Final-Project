import pytest
import json
import os
from pathlib import Path
from shop.service import ShopService

@pytest.fixture
def temp_data_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("data")

@pytest.fixture
def sample_catalog():
    return {
        "products": [
            {"id": "P001", "type": "piece", "name": "Кружка", "category": "merch", "price": 590, "stock": 10},
            {"id": "P003", "type": "piece", "name": "Кофе", "category": "coffee", "price": 790, "stock": 5},
            {"id": "P010", "type": "weight", "name": "Чай", "category": "tea", "price_per_kg": 2400, "min_kg": 0.1, "stock_kg": 3.5},
            {"id": "P020", "type": "digital", "name": "Курс", "category": "courses", "price": 1990}
        ]
    }

@pytest.fixture
def sample_promos():
    return {
        "promos": [
            {"code": "SALE10", "type": "percent", "percent": 10},
            {"code": "MINUS500", "type": "fixed", "amount": 500, "min_total": 3000},
            {"code": "COFFEE3", "type": "three_for_two", "category": "coffee"}
        ]
    }

@pytest.fixture
def service(temp_data_dir, sample_catalog, sample_promos):
    catalog_path = temp_data_dir / "catalog.json"
    promos_path = temp_data_dir / "promos.json"
    orders_path = temp_data_dir / "orders.json"

    catalog_path.write_text(json.dumps(sample_catalog, ensure_ascii=False, indent=2))
    promos_path.write_text(json.dumps(sample_promos, ensure_ascii=False, indent=2))
    orders_path.write_text(json.dumps({"cart": {"items": [], "promo": None}, "orders": [], "next_order_id": 1}))

    return ShopService(data_dir=str(temp_data_dir))