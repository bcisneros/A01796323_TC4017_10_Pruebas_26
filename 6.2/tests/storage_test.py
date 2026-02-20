"""JsonStore tests for file-backed load/save operations.

Covers:
- missing file -> empty list
- save then load round-trip
- corrupted JSON -> logs error and returns empty list
- save overwrites existing content
"""

# Keep tests lightweight—method names tell the story.
# Document at module/class level; avoid noisy method docstrings.
# pylint: disable=missing-function-docstring

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path

from reservation.storage import JsonStore


class StoreTest(unittest.TestCase):
    """Tests for the JSON-backed storage adapter (JsonStore)."""

    def setUp(self):
        # Manage resource-allocating ops via ExitStack (satisfies pylint R1732)
        self._stack = ExitStack()
        self.addCleanup(self._stack.close)

        # Per-test temp dir
        self.tmp = self._stack.enter_context(tempfile.TemporaryDirectory())
        self.base = Path(self.tmp)
        self.store = JsonStore(self.base)

    def test_load_missing_file_returns_empty_list(self):
        rows = self.store.load("hotels.json")  # file does not exist
        self.assertEqual([], rows)

    def test_save_then_load_round_trip_ok(self):
        data = [{"id": "H1", "name": "Hotel Azul", "rooms": 3}]
        self.store.save("hotels.json", data)

        out = self.store.load("hotels.json")
        self.assertEqual(data, out)

    def test_load_invalid_json_logs_and_returns_empty_list(self):
        # Create an invalid JSON file
        file = "customers.json"
        content = "{ BAD JSON ]"
        (self.base / file).write_text(content, encoding="utf-8")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rows = self.store.load("customers.json")

        self.assertEqual([], rows)
        log = buf.getvalue()
        self.assertIn("invalid JSON", log)
        self.assertIn("Continuing with empty list", log)

    def test_save_overwrites_existing_file(self):
        path = self.base / "reservations.json"
        path.write_text('["stale"]', encoding="utf-8")

        fresh = [
            {
                "id": "R1",
                "hotel_id": "H1",
                "customer_id": "C1",
                "room_number": 1
            }
        ]
        self.store.save("reservations.json", fresh)

        reloaded = self.store.load("reservations.json")
        self.assertEqual(fresh, reloaded)
