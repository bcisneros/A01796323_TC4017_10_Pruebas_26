from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import json

class JsonStore:
    """Simple JSON-file store for lists of dicts with error resilience."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)

    def _file(self, name: str) -> Path:
        return self.base_path / name

    def load(self, name: str) -> List[Dict]:
        file_path = self._file(name)
        if not file_path.exists():
            return []
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            # Req 5: manejar datos inválidos en archivo: reportar y continuar
            print(f"[ERROR] {name}: invalid JSON ({exc}); continuing with empty list")
            return []

    def save(self, name: str, rows: List[Dict]) -> None:
        self._file(name).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")