from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any
# from .exceptions import InvalidQuantityError, OutOfStockError

class Product(ABC):
    def __init__(self, product_id: str, name: str, category: str, price: Decimal, stock: Optional[Decimal]):
        # Переименовано из 'id' в 'product_id', чтобы не затенять built-in функцию id()
        self.product_id = product_id
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": str(self.price), # Decimal не сериализуется в JSON напрямую, превращаем в строку
            "stock": str(self.stock) if self.stock is not None else None
        }


class PieceProduct(Product):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def line_price(self, qty: Decimal) -> Decimal:
        return (self.price * qty).quantize(Decimal('0.01'))

    def check_qty(self, qty: Decimal):
        # Исключения должны импортироваться здесь, если они используются
        from .exceptions import InvalidQuantityError, OutOfStockError

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
            from .exceptions import InvalidQuantityError
            raise InvalidQuantityError(f"Минимальный вес: {self.min_kg} кг")
        total = self.price_per_kg * qty
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def check_qty(self, qty: Decimal):
        from .exceptions import InvalidQuantityError, OutOfStockError

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
            from .exceptions import InvalidQuantityError
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1")
        return self.price

    def check_qty(self, qty: Decimal):
        from .exceptions import InvalidQuantityError

        if qty != 1:
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1")