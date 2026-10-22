import json
import os
from typing import Any, Dict

class Repository:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Если файла нет, создаем его с пустым объектом, а не пустотой
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def load(self) -> Dict[str, Any]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                # Если файл пустой (0 байт), json.load() упадет. Возвращаем пустой dict.
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            # Если файл содержит битый JSON (не пустоту), даем понятную ошибку
            raise ValueError(f"Файл {self.path} поврежден или имеет неверный формат.")

    def save(self, data: Dict[str, Any]):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)