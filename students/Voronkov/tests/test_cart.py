import pytest
from decimal import Decimal as D
from shop.cart import Cart
from shop.exceptions import InvalidQuantityError, OutOfStockError, ProductNotFoundError


class DummyService:

    def __init__(self, products):
        self._products = products

    def get_product(self, pid):
        if pid not in self._products:
            raise ProductNotFoundError("Not found")
        return self._products[pid]


@pytest.fixture
def products():
    from shop.products import PieceProduct, WeightProduct, DigitalProduct
    return {
        # Штучный товар
        "P001": PieceProduct(
            product_id="P001", name="Кружка", category="merch",
            price=D("590"), stock=10),

        # Весовой товар
        "P010": WeightProduct(
            product_id="P010", name="Чай", category="tea",
            price=D("2400"), stock=D("3.5"), min_kg=D("0.1")),

        # Цифровой товар
        "P020": DigitalProduct(
            product_id="P020", name="Курс", category="courses",
            price=D("1990"), stock=None)  # У цифровых нет склада
    }


@pytest.fixture
def cart(products):
    return Cart(DummyService(products))


# Тесты добавления
def test_add_piece_success(cart):
    cart.add("P001", D('2'))
    assert len(cart) == 1
    assert cart.items[0].qty == D('2')
    assert cart.items[0].line_total == D('1180.00')


def test_add_piece_repeat_increments_qty(cart):
    cart.add("P001", D('1'))  # Строго Decimal
    cart.add("P001", D('2'))
    assert len(cart) == 1
    assert cart.items[0].qty == D('3')


def test_add_piece_invalid_qty_float(cart):
    with pytest.raises(InvalidQuantityError, match="целым"):
        cart.add("P001", D('1.5'))


def test_add_piece_out_of_stock(cart):
    with pytest.raises(OutOfStockError):
        cart.add("P001", D('11'))


def test_add_weight_success(cart):
    cart.add("P010", D('0.5'))
    assert cart.items[0].qty == D('0.5')
    assert cart.items[0].line_total == D('1200.00')


def test_add_weight_below_min(cart):
    with pytest.raises(InvalidQuantityError, match="Минимальный вес"):
        cart.add("P010", D('0.05'))


def test_add_digital_success(cart):
    cart.add("P020", D('1'))
