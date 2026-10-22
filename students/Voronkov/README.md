# Консольный интернет-магазин

Консольное приложение на Python 3.10+ с хранением данных в JSON, композицией сервисов и полным покрытием pytest.

## Установка
1. Создайте виртуальное окружение: `python -m venv venv && source venv/bin/activate`
2. Установите зависимости: `pip install -r requirements.txt`

## Подготовка данных
Убедитесь, что в папке `data/` лежат файлы:
* `catalog.json` — товары.
* `promos.json` — промокоды (только чтение).
* `orders.json` — может быть пустым `{}` или отсутствовать (создастся автоматически).

## Команды (CLI)

### Каталог
* `python main.py catalog --category coffee` — фильтр по категории.
* `python main.py search кофе` — поиск по подстроке.
* `python main.py show P003` — карточка товара.

### Корзина
* `python main.py cart add P003 2` — добавить 2 штуки.
* `python main.py cart add P010 0.35` — добавить 350г весового товара.
* `python main.py cart set P003 1` — изменить количество.
* `python main.py cart remove P003` — удалить позицию.
* `python main.py cart show` — состав корзины и суммы.

### Промокоды и заказы
* `python main.py promo SALE10` — применить промокод.
* `python main.py checkout` — оформить заказ (списывает остатки).
* `python main.py orders` — список заказов.
* `python main.py order 1` — детали заказа.
* `python main.py cancel 1` — отмена (возврат остатков).
* `python main.py restock P003 10` — приход товара.
* `python main.py export-orders reports/orders.csv` — выгрузка в CSV.

## Тесты
Запуск: `pytest -v`.
Тесты используют временные файлы и не трогают ваши данные в `data/`.

## Логирование
Все значимые действия записываются в `data/shop.log`.