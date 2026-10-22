import pytest
from decimal import Decimal
from shop.products import PieceProduct, WeightProduct, DigitalProduct
from shop.exceptions import OutOfStockError, InvalidQuantityError

def test_piece_line_price():
    p = PieceProduct(id="P1", name="A", category="c", price=100, stock=10)
    assert p.line_price(2) == Decimal('200.00')

def test_weight_rounding():
    p = WeightProduct(id="P2", name="B", category="c", price=1000, stock=10, min_kg=0.1)
    # 1000 * 0.333 = 333.00
    assert p.line_price(Decimal('0.333')) == Decimal('333.00')

def test_weight_min_kg():
    p = WeightProduct(id="P2", name="B", category="c", price=1000, stock=10, min_kg=0.5)
    with pytest.raises(InvalidQuantityError):
        p.check_qty(Decimal('0.1'))

def test_piece_out_of_stock():
    p = PieceProduct(id="P3", name="C", category="c", price=100, stock=5)
    with pytest.raises(OutOfStockError):
        p.check_qty(6)

def test_digital_qty():
    p = DigitalProduct(id="P4", name="D", category="c", price=500, stock=None)
    with pytest.raises(InvalidQuantityError):
        p.check_qty(2)