"""JSON-backed storage utilities for the reservation system.

This module provides a small wrapper (`JsonStore`) around plain JSON files
to persist *lists of dictionaries* for simple CRUD-like operations.

Design goals:
- Keep I/O concerns isolated from business logic (services).
- Be resilient to malformed JSON files: when decoding fails, log the error
  and continue with an empty list (so the application can keep running).
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import json


class JsonStore:
    """Tiny JSON-file store for lists of dicts with error resilience.

    Each logical collection (e.g., hotels, customers, reservations) is mapped
    to a single JSON file that contains a list of dictionary rows.
    """

    def __init__(self, base_path: Path) -> None:
        """Create a store rooted at `base_path`.

        Args:
            base_path: Directory where collection JSON files live.
        """
        self.base_path = Path(base_path)

    def _file(self, name: str) -> Path:
        """Return the absolute path for the given collection file name.

        Args:
            name: File name (e.g., 'hotels.json').

        Returns:
            Path: Absolute path to the target JSON file within `base_path`.
        """
        return self.base_path / name

    def load(self, name: str) -> List[Dict]:
        """Load a list of dictionaries from the named JSON file.

        Behavior:
        - If the file does not exist, an empty list is returned.
        - If the file contents are not valid JSON, an error message is printed
          and an empty list is returned (execution continues).

        Args:
            name: File name to load (e.g., 'customers.json').

        Returns:
            list[dict]: Parsed list from the JSON file, or [] if missing/invalid.
        """
        file_path = self._file(name)
        if not file_path.exists():
            return []
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            # Requirement: handle invalid data gracefully and continue
            print(f"[ERROR] {name}: invalid JSON ({exc})")
            print("[WARN] Continuing with empty list")
            return []

    def save(self, name: str, rows: List[Dict]) -> None:
        """Persist the given list of dictionaries into the named JSON file.

        Args:
            name: File name to write (e.g., 'reservations.json').
            rows: List of dictionary records to serialize.
        """
        self._file(name).write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
