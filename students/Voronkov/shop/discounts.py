from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cart import Cart


class Discount(ABC):
    @abstractmethod
    def apply(self, cart: "Cart") -> Decimal:
        pass


class PercentDiscount(Discount):
    def __init__(self, percent: int):
        self.percent = Decimal(percent)

    def apply(self, cart) -> Decimal:
        return (cart.subtotal * self.percent / 100).quantize(Decimal('0.01'))


class FixedFromThresholdDiscount(Discount):
    def __init__(self, amount: int, min_total: int):
        self.amount = Decimal(amount)
        self.min_total = Decimal(min_total)

    def apply(self, cart) -> Decimal:
        if cart.subtotal >= self.min_total:
            return min(self.amount, cart.subtotal)
        return Decimal('0.00')


class ThreeForTwoDiscount(Discount):
    def __init__(self, category: str):
        self.category = category

    def apply(self, cart) -> Decimal:
        discount = Decimal('0.00')
        from collections import defaultdict
        counts = defaultdict(Decimal)
        for item in cart.items:
            product = cart.service.get_product(item.product_id)
            if product.category == self.category and isinstance(product,
                                                                    type(cart.service.get_product(item.product_id))):
                if hasattr(product, 'stock') and product.stock is not None:
                    counts[item.product_id] += item.qty

        for prod_id, total_qty in counts.items():
            product = cart.service.get_product(prod_id)
            free_sets = int(total_qty // 3)
            discount += (product.price * free_sets).quantize(Decimal('0.01'))
        return discount


class CategoryPercentDiscount(Discount):
    def __init__(self, category: str, percent: int):
        self.category = category
        self.percent = Decimal(percent)

    def apply(self, cart) -> Decimal:
        discount = Decimal('0.00')
        for item in cart.items:
            product = cart.service.get_product(item.product_id)
            if product.category == self.category:
                discount += (item.line_total * self.percent / 100).quantize(Decimal('0.01'))
        return discount


class DiscountFactory:
    @staticmethod
    def create(data: dict):
        type_map = {
            "percent": PercentDiscount,
            "fixed": FixedFromThresholdDiscount,
            "three_for_two": ThreeForTwoDiscount,
            "category_percent": CategoryPercentDiscount
        }
        cls = type_map.get(data["type"])
        if not cls:
            raise ValueError(f"Неизвестный тип промокода: {data['type']}")

        if data["type"] == "percent":
            return cls(data["percent"])
        if data["type"] == "fixed":
            return cls(data["amount"], data["min_total"])
        if data["type"] == "three_for_two":
            return cls(data["category"])
        if data["type"] == "category_percent":
            return cls(data["category"], data["percent"])

        return cls()