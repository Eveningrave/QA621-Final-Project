import pytest
from decimal import Decimal as D
from shop.cart import Cart, CartItem
from shop.discounts import DiscountFactory


class DummyService:
    """Заглушка сервиса"""

    piece_price = D("590")
    weight_price = D("2400")
    digital_price = D("1990")

    @staticmethod
    def get_product(product_id):
        from shop.products import DigitalProduct, PieceProduct, WeightProduct

        if product_id == "P010" or "weight" in product_id.lower():
            return WeightProduct(
                product_id=product_id,
                name=f"{product_id} (весовой)",
                category="tea",
                price=D("2400"),
                stock=D("3.5"),
                min_kg=D("0.1"))
        elif product_id == "P020" or "digital" in product_id.lower():
            return DigitalProduct(
                product_id=product_id,
                name=f"{product_id} (цифровой)",
                category="courses",
                price=D("1990"),
                stock=None)
        else:
            return PieceProduct(
                product_id=product_id,
                name=f"{product_id} (штучный)",
                category="merch",
                price=D("590"),
                stock=10)


def test_percent_discount():
    cart = Cart(DummyService())
    cart.items.append(CartItem(product_id="P1", qty=D('1'), price=D('100'), line_total=D('100')))
    cart.items.append(CartItem(product_id="P2", qty=D('2'), price=D('100'), line_total=D('200')))

    promo = DiscountFactory.create({
        "type": "percent",
        "code": "SALE_10_TEST",
        "percent": 10
    })
    assert promo.apply(cart) == D('30.00')


def test_fixed_threshold_not_met():
    cart = Cart(DummyService())
    cart.items.append(CartItem(product_id="P1", qty=D('1'), price=D('100'), line_total=D('100')))

    promo = DiscountFactory.create({
        "type": "fixed",
        "code": "MINUS_500_TEST",
        "amount": 500,
        "min_total": 3000
    })
    assert promo.apply(cart) == D('0.00')


def test_fixed_threshold_met():
    cart = Cart(DummyService())
    cart.items.append(CartItem(product_id="P1", qty=D('1'), price=D('3500'), line_total=D('3500')))

    promo = DiscountFactory.create({
        "type": "fixed",
        "code": "MINUS_500_TEST",
        "amount": 500,
        "min_total": 3000
    })
    assert promo.apply(cart) == D('500.00')


def test_three_for_two():
    cart = Cart(DummyService())
    cart.items.append(CartItem(product_id="P010", qty=D('3'), price=D('100'), line_total=D('300')))
    cart.items.append(CartItem(product_id="P020", qty=D('2'), price=D('200'), line_total=D('400')))

    promo = DiscountFactory.create({
        "type": "three_for_two",
        "code": "COFFEE3_TEST",
        "category": "tea"
    })
    assert promo.apply(cart) == D('100.00')


def test_category_percent():
    cart = Cart(DummyService())
    cart.items.append(CartItem(product_id="P010", qty=D('1'), price=D('100'), line_total=D('100')))
    cart.items.append(CartItem(product_id="P020", qty=D('1'), price=D('200'), line_total=D('200')))

    promo = DiscountFactory.create({
        "type": "category_percent",
        "code": "CATPERC_TEST",
        "category": "tea",
        "percent": 10
    })
    assert promo.apply(cart) == D('10.00')


def test_factory_unknown_type():
    with pytest.raises(ValueError):
        DiscountFactory.create({"type": "unknown_type"})