from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

class Product(ABC):
    def __init__(self, id: str, name: str, category: str, price: Decimal, stock: Optional[Decimal]):
        self.id = id
        self._name = name
        self._category = category
        self._price = Decimal(price)
        self._stock = Decimal(stock) if stock is not None else None

    @property
    def name(self):
        return self._name

    @property
    def category(self):
        return self._category

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value <= 0:
            raise ValueError("Цена должна быть больше нуля")
        self._price = Decimal(value)

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value):
        if value < 0:
            raise ValueError("Остаток не может быть отрицательным")
        self._stock = Decimal(value)

    @abstractmethod
    def line_price(self, qty: Decimal) -> Decimal:
        pass

    @abstractmethod
    def check_qty(self, qty: Decimal):
        pass

    def to_dict(self):
        return asdict(self)

class PieceProduct(Product):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def line_price(self, qty: Decimal) -> Decimal:
        return (self.price * qty).quantize(Decimal('0.01'))

    def check_qty(self, qty: Decimal):
        if not qty == int(qty):
            raise InvalidQuantityError("Количество штучного товара должно быть целым")
        if qty <= 0:
            raise InvalidQuantityError("Количество должно быть больше нуля")
        if qty > self.stock:
            raise OutOfStockError(f"Недостаточно товара на складе (осталось {self.stock})")

class WeightProduct(Product):
    def __init__(self, min_kg: Decimal, **kwargs):
        super().__init__(**kwargs)
        self.min_kg = Decimal(min_kg)

    @property
    def price_per_kg(self):
        return self.price

    @price_per_kg.setter
    def price_per_kg(self, value):
        self.price = value

    def line_price(self, qty: Decimal) -> Decimal:
        if qty < self.min_kg:
            raise InvalidQuantityError(f"Минимальный вес: {self.min_kg} кг")
        total = self.price_per_kg * qty
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def check_qty(self, qty: Decimal):
        if qty <= 0:
            raise InvalidQuantityError("Количество должно быть больше нуля")
        if qty < self.min_kg:
            raise InvalidQuantityError(f"Минимальный вес: {self.min_kg} кг")
        if qty > self.stock:
            raise OutOfStockError(f"Недостаточно товара на складе (осталось {self.stock} кг)")

class DigitalProduct(Product):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def line_price(self, qty: Decimal) -> Decimal:
        if qty != 1:
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1")
        return self.price

    def check_qty(self, qty: Decimal):
        if qty != 1:
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1")