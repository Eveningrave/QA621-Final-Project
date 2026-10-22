from decimal import Decimal
from shop.cart import Cart, CartItem
from shop.discounts import DiscountFactory
from shop.products import PieceProduct

class DummyService:
    def get_product(self, pid):
        return PieceProduct(id=pid, name="A", category="coffee", price=100, stock=10)

def test_percent_discount():
    cart = Cart(DummyService())
    cart.items.append(CartItem("P1", 1, 100, 100))
    promo = DiscountFactory.create({"type": "percent", "percent": 10})
    assert promo.apply(cart) == Decimal('10.00')

def test_fixed_threshold_not_met():
    cart = Cart(DummyService())
    cart.items.append(CartItem("P1", 1, 100, 100)) # Сумма 100
    promo = DiscountFactory.create({"type": "fixed", "amount": 500, "min_total": 3000})
    assert promo.apply(cart) == Decimal('0.00')

def test_three_for_two():
    cart = Cart(DummyService())
    cart.items.append(CartItem("P1", 3, 100, 300)) # 1 бесплатно
    cart.items.append(CartItem("P2", 2, 200, 400)) # Другая категория, не участвует
    promo = DiscountFactory.create({"type": "three_for_two", "category": "coffee"})
    assert promo.apply(cart) == Decimal('100.00')