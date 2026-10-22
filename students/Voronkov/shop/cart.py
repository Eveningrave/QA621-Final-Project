from dataclasses import dataclass, field, asdict
from decimal import Decimal
from typing import List, Optional
from .products import Product
from .discounts import Discount


@dataclass
class CartItem:
    product_id: str
    qty: Decimal
    price: Decimal
    line_total: Decimal


class Cart:
    def __init__(self, service):
        self.service = service
        self.items: List[CartItem] = []
        self.promo: Optional[Discount] = None

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, product_id: str):
        return any(item.product_id == product_id for item in self.items)

    def __bool__(self):
        return bool(self.items)

    @property
    def subtotal(self) -> Decimal:
        return sum(item.line_total for item in self.items)

    @property
    def discount(self) -> Decimal:
        if not self.promo:
            return Decimal('0.00')
        return self.promo.apply(self)

    @property
    def total(self) -> Decimal:
        return max(self.subtotal - self.discount, Decimal('0.00'))

    def add(self, product_id: str, qty: Decimal):
        product = self.service.get_product(product_id)
        product.check_qty(qty)

        for item in self.items:
            if item.product_id == product_id:
                new_qty = item.qty + qty
                product.check_qty(new_qty)
                item.qty = new_qty
                item.price = product.price if not isinstance(product, WeightProduct) else product.price_per_kg
                item.line_total = product.line_price(new_qty)
                return

        self.items.append(CartItem(
            product_id=product_id,
            qty=qty,
            price=product.price if not isinstance(product, WeightProduct) else product.price_per_kg,
            line_total=product.line_price(qty)
        ))

    def set_qty(self, product_id: str, qty: Decimal):
        if qty == 0:
            self.remove(product_id)
            return
        product = self.service.get_product(product_id)
        product.check_qty(qty)
        for item in self.items:
            if item.product_id == product_id:
                item.qty = qty
                item.line_total = product.line_price(qty)
                return
        raise ProductNotFoundError("Товар не в корзине")

    def remove(self, product_id: str):
        self.items = [i for i in self.items if i.product_id != product_id]

    def apply_promo(self, code: str):
        promos = self.service.load_promos()
        promo_data = next((p for p in promos if p["code"] == code), None)
        if not promo_data:
            raise InvalidPromoError("Промокод не найден")

        factory = DiscountFactory()
        self.promo = factory.create(promo_data)

    def clear(self):
        self.items = []
        self.promo = None