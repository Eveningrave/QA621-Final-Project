import pytest
from decimal import Decimal as D
# Импортируем ТОЛЬКО сами классы товаров
from shop.products import DigitalProduct, PieceProduct, WeightProduct


def test_piece_line_price():
    p = PieceProduct(
        product_id="P1",
        name="A",
        category="coffee",
        price=D("100"),
        stock=10
    )
    assert p.line_price(D('2')) == D('200.00')


def test_weight_rounding():
    """
    Проверка банковского округления до копеек.
    При цене 1000 ₽/кг и весе 0.333 итоговая сумма должна быть ровно 333 ₽.
    """
    p = WeightProduct(
        product_id="P2",
        name="B",
        category="tea",
        price=D("1000"),
        stock=D("10"),
        min_kg=D("0.1")
    )
    assert p.line_price(D('0.333')) == D('333.00')


def test_weight_min_kg():
    """
    Тест минимального веса.
    Если товар имеет порог 0.5 кг, попытка добавить 0.1 кг должна вызвать исключение.
    """
    p = WeightProduct(
        product_id="P2",
        name="B",
        category="tea",
        price=D("1000"),
        stock=D("10"),
        min_kg=D("0.5")  # <-- Минимальный вес
    )

    # Локально импортировали КОНКРЕТНОЕ исключение
    from shop.exceptions import InvalidQuantityError

    with pytest.raises(InvalidQuantityError):
        p.check_qty(D('0.1'))


def test_piece_out_of_stock():
    """
    Штучный товар нельзя купить больше, чем есть на складе.
    """
    p = PieceProduct(
        product_id="P3",
        name="C",
        category="merch",
        price=D("100"),
        stock=D("5")
    )

    # Локально импортировали КОНКРЕТНОЕ исключение
    from shop.exceptions import OutOfStockError

    with pytest.raises(OutOfStockError):
        p.check_qty(D('6'))


def test_digital_qty():
    """
    Цифровой товар можно купить только в количестве 1.
    Попытка добавить две штуки должна вызвать ошибку.
    """
    p = DigitalProduct(
        product_id="P4",
        name="D",
        category="courses",
        price=D("500"),
        stock=None  # У цифровых нет склада
    )

    from shop.exceptions import InvalidQuantityError

    with pytest.raises(InvalidQuantityError):
        p.check_qty(D('2'))