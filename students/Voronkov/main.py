import sys
import argparse
from decimal import Decimal
from shop.service import ShopService
from shop.exceptions import ShopError


def main():
    service = ShopService()
    parser = argparse.ArgumentParser(prog="shop")
    sub = parser.add_subparsers(dest="command", required=True)

    # Каталог
    cat = sub.add_parser("catalog")
    cat.add_argument("--category")
    search = sub.add_parser("search")
    search.add_argument("query")
    show = sub.add_parser("show")
    show.add_argument("id")

    # Корзина
    csub = sub.add_parser("cart").add_subparsers(dest="action", required=True)
    cadd = csub.add_parser("add")
    cadd.add_argument("id");
    cadd.add_argument("qty")
    cset = csub.add_parser("set")
    cset.add_argument("id");
    cset.add_argument("qty")
    crem = csub.add_parser("remove")
    crem.add_argument("id")
    cshow = csub.add_parser("show")

    # Промо
    promo = sub.add_parser("promo")
    promo.add_argument("code")

    # Заказы
    sub.add_parser("checkout")
    sub.add_parser("orders")
    order = sub.add_parser("order")
    order.add_argument("id")
    cancel = sub.add_parser("cancel")
    cancel.add_argument("id")
    restock = sub.add_parser("restock")
    restock.add_argument("id");
    restock.add_argument("qty")
    export = sub.add_parser("export-orders")
    export.add_argument("path")

    args = parser.parse_args()

    try:
        if args.command == "catalog":
            items = service.list_products(args.category)
            for p in items:
                print(f"{p.id} | {p.name} | {p.category} | {p.price} ₽ | {p.stock}")
        elif args.command == "search":
            items = service.search_products(args.query)
            for p in items:
                print(f"{p.id} | {p.name}")
        elif args.command == "show":
            p = service.get_product(args.id)
            print(f"{p.id} | {p.name} | {p.category} | {p.price} ₽ | {p.stock}")
            if hasattr(p, 'min_kg'):
                print(f"Тип: весовой, мин. {p.min_kg} кг")

        elif args.command == "cart":
            if args.action == "add":
                service.add_to_cart(args.id, Decimal(args.qty))
                print("Добавлено в корзину")
            elif args.action == "set":
                service.cart.set_qty(args.id, Decimal(args.qty))
                service._save_state()
                print("Количество обновлено")
            elif args.action == "remove":
                service.cart.remove(args.id)
                service._save_state()
                print("Удалено из корзины")
            elif args.action == "show":
                if not service.cart:
                    print("Корзина пуста")
                else:
                    for i in service.cart:
                        print(f"{i.product_id} x{i.qty} = {i.line_total} ₽")
                    print(f"Итого: {service.cart.subtotal} ₽")
                    if service.cart.discount > 0:
                        print(f" Скидка: {service.cart.discount} ₽")
                    print(f"ИТОГ: {service.cart.total} ₽")
                    if service.cart.promo:
                        print(f"Промокод: {service.cart.promo.code}")

        elif args.command == "promo":
            try:
                service.cart.apply_promo(args.code)
                service._save_state()
                print(f"Применен промокод {args.code}")
            except ShopError as e:
                print(e)

        elif args.command == "checkout":
            order = service.checkout()
            print("Заказ оформлен:")
            print(order)

        elif args.command == "orders":
            for o in service.orders:
                print(f"#{o.id} | {o.status} | {o.total} ₽")

        elif args.command == "order":
            o = next((x for x in service.orders if x.id == int(args.id)), None)
            if o:
                print(o)
            else:
                print("Заказ не найден")

        elif args.command == "cancel":
            service.cancel_order(int(args.id))
            print("Заказ отменен")

        elif args.command == "restock":
            service.restock(args.id, Decimal(args.qty))
            print("Остаток обновлен")

        elif args.command == "export-orders":
            import csv
            with open(args.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "status", "items_count", "subtotal", "discount", "total"])
                for o in service.orders:
                    writer.writerow([o.id, o.status, len(o.items), o.subtotal, o.discount, o.total])
            print(f"Экспортировано в {args.path}")

    except ShopError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()



