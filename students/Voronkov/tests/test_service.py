import pytest
from decimal import Decimal
from shop.exceptions import OutOfStockError, EmptyCartError


def test_checkout_decreases_stock(service):
    service.add_to_cart("P003", 2)
    order = service.checkout()
    assert order.total > 0
    assert service.get_product("P003").stock == 3  # Было 5, списали 2


def test_checkout_insufficient_stock_does_not_change_warehouse(service):
    # В фикстуре stock у P003 = 5
    service.add_to_cart("P003", 10)  # Должно кинуть исключение до списания
    with pytest.raises(OutOfStockError):
        service.checkout()
    # Склад не изменился
    assert service.get_product("P003").stock == 5


def test_cancel_order_returns_stock(service):
    service.add_to_cart("P003", 2)
    order = service.checkout()
    assert service.get_product("P003").stock == 3

    service.cancel_order(order.id)
    assert service.get_product("P003").stock == 5  # Вернулось 2
    assert service.orders[0].status == "cancelled"


def test_double_cancel_raises(service):
    service.add_to_cart("P003", 1)
    order = service.checkout()
    service.cancel_order(order.id)
    with pytest.raises(Exception):
        service.cancel_order(order.id)