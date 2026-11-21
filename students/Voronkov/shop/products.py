from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any
from .exceptions import InvalidQuantityError, OutOfStockError


class Product(ABC):
    def __init__(self, product_id: str, name: str, category: str, price: Decimal, stock: Optional[Decimal]):
        self.product_id = product_id
        self._name = name
        self._category = category
        self._price = Decimal(str(price))
        self._stock = Decimal(str(stock)) if stock is not None else None

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
        if Decimal(str(value)) <= 0:
            raise ValueError("Цена должна быть больше нуля")
        self._price = Decimal(str(value))

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value):
        if value is None:
            self._stock = None
            return
        if Decimal(str(value)) < 0:
            raise ValueError("Остаток не может быть отрицательным")
        self._stock = Decimal(str(value))

    @abstractmethod
    def line_price(self, qty: Decimal) -> Decimal:
        pass

    @abstractmethod
    def check_qty(self, qty: Decimal):
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


class PieceProduct(Product):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def line_price(self, qty: Decimal) -> Decimal:
        return (self.price * qty).quantize(Decimal('0.01'))

    def check_qty(self, qty: Decimal):
        if qty % 1 != 0:
            raise InvalidQuantityError("Количество штучного товара должно быть целым")
        if qty <= 0:
            raise InvalidQuantityError("Количество должно быть больше нуля")
        if self.stock is not None and qty > self.stock:
            raise OutOfStockError(f"Недостаточно товара на складе (осталось {self.stock})")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.product_id,
            "type": "piece",
            "name": self.name,
            "category": self.category,
            "price": str(self.price),
            "stock": str(self.stock) if self.stock is not None else None
        }


class WeightProduct(Product):
    def __init__(self, min_kg: Decimal, **kwargs):
        super().__init__(**kwargs)
        self.min_kg = Decimal(str(min_kg))

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
        if self.stock is not None and qty > self.stock:
            raise OutOfStockError(f"Недостаточно товара на складе (осталось {self.stock} кг)")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.product_id,
            "type": "weight",
            "name": self.name,
            "category": self.category,
            "price_per_kg": str(self.price),
            "stock_kg": str(self.stock) if self.stock is not None else None,
            "min_kg": str(self.min_kg)
        }


class DigitalProduct(Product):
    def __init__(self, **kwargs):
        # У цифрового товара нет склада, поэтому принудительно ставим stock=None
        kwargs["stock"] = None
        super().__init__(**kwargs)

    def line_price(self, qty: Decimal) -> Decimal:
        if qty != 1:
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1")
        return self.price

    def check_qty(self, qty: Decimal):
        if qty != 1:
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.product_id,
            "type": "digital",
            "name": self.name,
            "category": self.category,
            "price": str(self.price),
            "stock": None
        }