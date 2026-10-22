
import json
import os
from decimal import Decimal
from typing import List, Optional
from .repository import Repository
from .products import PieceProduct, WeightProduct, DigitalProduct
from .cart import Cart, CartItem
from .orders import Order
from .decorators import log_action
from .exceptions import *

PRODUCT_CLASSES = {
    "piece": PieceProduct,
    "weight": WeightProduct,
    "digital": DigitalProduct
}


class ShopService:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.catalog_repo = Repository(os.path.join(data_dir, "catalog.json"))
        self.promos_repo = Repository(os.path.join(data_dir, "promos.json"))
        self.orders_repo = Repository(os.path.join(data_dir, "orders.json"))

        self._load_catalog()
        self.cart = Cart(self)
        self._load_cart_and_orders()

    def _load_catalog(self):
        data = self.catalog_repo.load()
        self.products = {}
        for p in data.get("products", []):
            cls = PRODUCT_CLASSES[p["type"]]
            if p["type"] == "weight":
                self.products[p["id"]] = cls(
                    id=p["id"], name=p["name"], category=p["category"],
                    price=p["price_per_kg"], stock=p["stock_kg"],
                    min_kg=p["min_kg"]
                )
            else:
                self.products[p["id"]] = cls(
                    id=p["id"], name=p["name"], category=p["category"],
                    price=p["price"], stock=p.get("stock")
                )

    def _save_catalog(self):
        payload = {"products": [p.to_dict() for p in self.products.values()]}
        self.catalog_repo.save(payload)


    def _load_cart_and_orders(self):
        data = self.orders_repo.load()

        cart_items_data = []
        cart_promo = None
        orders_data = []
        next_id = 1

        if data:
            cart_items_data = data.get("cart", {}).get("items", [])
            cart_promo = data.get("cart", {}).get("promo")
            orders_data = data.get("orders", [])
            next_id = data.get("next_order_id", 1)

        self.cart.items = []
        for item_data in cart_items_data:
            try:
                product = self.get_product(item_data["product_id"])
                self.cart.items.append(
                    CartItem(
                        **item_data,
                        line_total=product.line_price(item_data["qty"])
                    )
                )
            except (ProductNotFoundError, KeyError):
                continue

            if cart_promo:
                try:
                    self.cart.apply_promo(cart_promo)
                except Exception:
                    self.cart.promo = None

            # Загрузка заказов
            self.orders = []
            for o in orders_data:
                try:
                    items = [CartItem(**i) for i in o["items"]]
                    self.orders.append(Order(**o, items=items))
                except (KeyError, TypeError):
                    continue

            self.next_order_id = next_id


        # Загрузка заказов
        self.orders = []
        for o in data.get("orders", []):
            items = [CartItem(**i) for i in o["items"]]
            self.orders.append(Order(**o, items=items))

        self.next_order_id = data.get("next_order_id", 1)

    def _save_orders(self):
        cart_data = {
            "items": [item.__dict__ for item in self.cart.items],
            "promo": self.cart.promo.code if self.cart.promo else None
        }
        orders_data = {
            "cart": cart_data,
            "orders": [
                {
                    **order.__dict__,
                    "items": [item.__dict__ for item in order.items]
                }
                for order in self.orders
            ],
            "next_order_id": self.next_order_id
        }
        self.orders_repo.save(orders_data)

    def get_product(self, product_id: str):
        if product_id not in self.products:
            raise ProductNotFoundError(f"Товар {product_id} не найден")
        return self.products[product_id]

    def list_products(self, category: str = None):
        return [p for p in self.products.values() if category is None or p.category == category]

    def search_products(self, query: str):
        q = query.lower()
        return [p for p in self.products.values() if q in p.name.lower()]

    @log_action
    def add_to_cart(self, product_id: str, qty):
        self.cart.add(product_id, Decimal(str(qty)))
        self._save_orders()

    @log_action
    def checkout(self):
        if not self.cart:
            raise EmptyCartError("Корзина пуста")

        # Проверка остатков
        for item in self.cart.items:
            product = self.get_product(item.product_id)
            if not isinstance(product, DigitalProduct):
                product.check_qty(item.qty)

        # Списание и сохранение КАТАЛОГА
        for item in self.cart.items:
            product = self.get_product(item.product_id)
            if not isinstance(product, DigitalProduct):
                product.stock -= item.qty
        self._save_catalog()

        # Создание заказа
        order = Order(
            id=self.next_order_id,
            items=self.cart.items.copy(),
            subtotal=self.cart.subtotal,
            discount=self.cart.discount,
            total=self.cart.total,
            promo=self.cart.promo.code if self.cart.promo else None
        )
        self.orders.append(order)
        self.next_order_id += 1

        # Очистка корзины и сохранение ЗАКАЗОВ
        self.cart.clear()
        self._save_orders()
        return order

    @log_action
    def cancel_order(self, order_id: int):
        order = next((o for o in self.orders if o.id == order_id), None)
        if not order:
            raise OrderNotFoundError(f"Заказ {order_id} не найден")
        if order.status == "cancelled":
            raise ShopError(f"Заказ {order_id} уже отменен")

        # Возврат на склад и сохранение КАТАЛОГА
        for item in order.items:
            product = self.get_product(item.product_id)
            if not isinstance(product, DigitalProduct):
                product.stock += item.qty
        self._save_catalog()

        order.status = "cancelled"
        self._save_orders()

    @log_action
    def restock(self, product_id: str, qty):
        product = self.get_product(product_id)
        if isinstance(product, DigitalProduct):
            raise ShopError("У цифрового товара нет склада")
        product.stock += Decimal(str(qty))
        self._save_catalog()

    def load_promos(self):
        return self.promos_repo.load().get("promos", [])