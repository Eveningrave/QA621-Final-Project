import functools
import logging
import os
from datetime import datetime

LOG_PATH = "data/shop.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger = logging.getLogger("shop")
if not logger.handlers:  # Защита от дублирования хендлеров
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        service = args[0] if args else None
        action = func.__name__
        params = {k: v for k, v in kwargs.items()}
        if len(args) > 1:
            params.update({f"arg_{i}": v for i, v in enumerate(args[1:], 1)})

        result = func(*args, **kwargs)

        if service and hasattr(service, 'cart'):
            cart_summary = f"items={len(service.cart)}, total={service.cart.total}"
            logger.info(f"{action} | {params} | cart: {cart_summary}")
        else:
            logger.info(f"{action} | {params}")

        return result

    return wrapper