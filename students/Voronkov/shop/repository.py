import json
import os
from decimal import Decimal
from typing import Any, Dict

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)  # Превращаем Decimal в строку, чтобы сохранить точность
        return super().default(o)

class Repository:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def load(self) -> Dict[str, Any]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Файл {self.path} поврежден или имеет неверный формат.")

    def save(self, data: Dict[str, Any]):
        with open(self.path, "w", encoding="utf-8") as f:
            # ДОБАВЬ СЮДА, БЛЯДЬ, КЛАСС ЭНКОДЕРА!
            json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)