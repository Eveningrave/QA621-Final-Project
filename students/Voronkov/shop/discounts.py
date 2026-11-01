from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cart import Cart


class Discount(ABC):
    def __init__(self, code: str):
        self.code = code

    @abstractmethod
    def apply(self, cart: "Cart") -> Decimal:
        pass


class PercentDiscount(Discount):
    def __init__(self, code: str, percent: int):
        super().__init__(code)
        self.percent = Decimal(percent)

    def apply(self, cart) -> Decimal:
        return (cart.subtotal * self.percent / 100).quantize(Decimal('0.01'))


class FixedFromThresholdDiscount(Discount):
    def __init__(self, code: str, amount: int, min_total: int):
        super().__init__(code)
        self.amount = Decimal(amount)
        self.min_total = Decimal(min_total)

    def apply(self, cart) -> Decimal:
        if cart.subtotal >= self.min_total:
            return min(self.amount, cart.subtotal)
        return Decimal('0.00')


class ThreeForTwoDiscount(Discount):
    def __init__(self, code: str, category: str):
        super().__init__(code)
        self.category = category

    def apply(self, cart) -> Decimal:
        discount = Decimal('0.00')
        items_info = {}

        for item in cart.items:
            product = cart.service.get_product(item.product_id)
            if product.category == self.category and product.stock is not None:
                if item.product_id not in items_info:
                    # Берём ЦЕНУ ИЗ КОРЗИНЫ (item.price), а не из сервиса, дебил!
                    items_info[item.product_id] = {"qty": Decimal('0'), "price": item.price}
                items_info[item.product_id]["qty"] += item.qty

        for prod_id, info in items_info.items():
            free_sets = int(info["qty"] // 3)
            discount += (info["price"] * free_sets).quantize(Decimal('0.01'))
        return discount


class CategoryPercentDiscount(Discount):
    def __init__(self, code: str, category: str, percent: int):
        super().__init__(code)
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
            return cls(data["code"], data["percent"])
        if data["type"] == "fixed":
            # ВОТ СЮДА, БЛЯДЬ, ЗАБЫЛ ПЕРЕДАТЬ CODE!
            return cls(data["code"], data["amount"], data["min_total"])
        if data["type"] == "three_for_two":
            return cls(data["code"], data["category"])
        if data["type"] == "category_percent":
            # И СЮДА ТОЖЕ, УЁБОК!
            return cls(data["code"], data["category"], data["percent"])

        raise ValueError(f"Неизвестный тип промокода: {data['type']}")