import os
import json
from decimal import Decimal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print

from shop.service import ShopService

console = Console()
DATA_DIR = "data"


def print_products(service: ShopService, category: str = None):
    products = service.list_products(category)
    if not products:
        print(f"[yellow]Товаров в категории '{category}' не найдено.[/yellow]")
        return

    table = Table(title=f"Товары{' (' + category + ')' if category else ''}")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Название", style="magenta")
    table.add_column("Категория", style="green")
    table.add_column("Цена", justify="right", style="yellow")
    table.add_column("Остаток", justify="right", style="red")

    for p in products:
        price_str = f"{p.price_per_kg} ₽/кг" if hasattr(p, 'price_per_kg') else f"{p.price} ₽"

        # Для остатка проверяем stock и min_kg через атрибуты
        if hasattr(p, 'min_kg'):
            stock_str = f"{p.stock} кг"
        elif p.stock is not None:
            stock_str = str(p.stock)
        else:
            stock_str = "∞"

        table.add_row(p.product_id, p.name, p.category, price_str, stock_str)

    console.print(table)


def print_cart(service: ShopService):
    if not service.cart:
        print(Panel("Корзина пуста", style="dim"))
        return

    table = Table(title="Ваша корзина")
    table.add_column("ID", style="cyan")
    table.add_column("Название", style="magenta")
    table.add_column("Кол-во", justify="right")
    table.add_column("Цена", justify="right")
    table.add_column("Сумма", justify="right", style="bold green")

    for item in service.cart.items:
        product = service.get_product(item.product_id)
        table.add_row(item.product_id, product.name, str(item.qty), f"{item.price} ₽", f"{item.line_total} ₽")

    table.add_section()
    table.add_row("", "", "", "[bold]Итого:[/bold]", f"[bold]{service.cart.subtotal} ₽[/bold]")
    if service.cart.discount > 0:
        table.add_row("", "", "", "[bold]Скидка:[/bold]", f"[bold]-{service.cart.discount} ₽[/bold]")
        table.add_row("", "", "", "[bold]К оплате:[/bold]", f"[bold]{service.cart.total} ₽[/bold]")

    console.print(table)


def print_orders(service: ShopService):
    if not service.orders:
        print(Panel("Заказов еще нет", style="dim"))
        return

    for order in service.orders:
        console.print(
            Panel(str(order), title=f"Заказ #{order.id}", border_style="green" if order.status == "new" else "dim"))


def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Инициализация файлов, если их нет
    init_files = ["catalog.json", "promos.json", "orders.json"]
    for filename in init_files:  
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            if filename == "catalog.json":
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"products": []}, f, ensure_ascii=False, indent=2)
            elif filename == "promos.json":
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"promos": []}, f, ensure_ascii=False, indent=2)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"cart": {"items": [], "promo": None}, "orders": [], "next_order_id": 1}, f,
                              ensure_ascii=False, indent=2)

    service = ShopService(DATA_DIR)

    print(Panel("[bold cyan]Добро пожаловать в Магазин[/bold cyan]", subtitle="Введите команду"))

    while True:
        try:
            cmd = Prompt.ask(
                "\nВведите команду ([bold]list[/bold], [bold]add[/bold], [bold]cart[/bold], [bold]promo[/bold], [bold]checkout[/bold], [bold]orders[/bold], [bold]cancel[/bold], [bold]exit[/bold])").lower()

            if cmd == "exit":
                print("До свидания!")
                break
            elif cmd == "list":
                cat = Prompt.ask("Категория (или Enter для всех)", default="")
                print_products(service, cat if cat else None)
            elif cmd == "add":
                pid = Prompt.ask("ID товара")
                try:
                    qty_input = Prompt.ask("Количество")
                    qty = Decimal(qty_input)
                    service.add_to_cart(pid, qty)
                    # ИСПРАВЛЕНО: Убрана ручная печать, теперь это делает @log_action в service.py
                    # А здесь мы подтверждаем действие пользователю
                    print(f"[green]Товар {pid} в количестве {qty} добавлен.[/green]")
                except Exception as e:
                    print(f"[red]Ошибка: {e}[/red]")
            elif cmd == "cart":
                print_cart(service)
            elif cmd == "promo":
                code = Prompt.ask("Промокод")
                try:
                    service.cart.apply_promo(code)
                    service._save_orders()  # Сохраняем состояние корзины после применения промокода
                    print(f"[green]Промокод {code} применен.[/green]")
                except Exception as e:
                    print(f"[red]Ошибка: {e}[/red]")
            elif cmd == "checkout":
                try:
                    order = service.checkout()
                    # ИСПРАВЛЕНО: Убрана ручная печать, логирование в service.py
                    print(Panel(str(order), title="Заказ оформлен!", border_style="green"))
                except Exception as e:
                    print(f"[red]Ошибка: {e}[/red]")
            elif cmd == "orders":
                print_orders(service)
            elif cmd == "cancel":
                oid = Prompt.ask("ID заказа для отмены", default="")
                if not oid:
                    continue
                try:
                    service.cancel_order(int(oid))
                    # ИСПРАВЛЕНО: Убрана ручная печать
                    print(f"[green]Заказ {oid} отменен.[/green]")
                except Exception as e:
                    print(f"[red]Ошибка: {e}[/red]")
            else:
                print("[yellow]Неизвестная команда.[/yellow]")
        except KeyboardInterrupt:
            print("\n[yellow]Выход...[/yellow]")
            break
        except Exception as e:
            print(f"[bold red]Критическая ошибка: {e}[/bold red]")


if __name__ == "__main__":
    main()