from dataclasses import dataclass, asdict, field
from decimal import Decimal
from typing import List
from .cart import CartItem

@dataclass
class Order:
    id: int
    items: List[CartItem]
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    promo: str
    status: str = "new"

    def __str__(self):
        lines = [f"Заказ #{self.id} ({self.status})"]
        for item in self.items:
            lines.append(f" - {item.product_id} x{item.qty} = {item.line_total} ₽")
        lines.append(f"Итого без скидки: {self.subtotal} ₽")
        if self.discount > 0:
            lines.append(f" скидка: {self.discount} ₽")
        lines.append(f"ИТОГ: {self.total} ₽")
        return "\n".join(lines)