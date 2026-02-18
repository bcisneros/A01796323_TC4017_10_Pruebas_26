"""Shared test utilities for JSON-backed reservation tests."""

from __future__ import annotations

import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path

from reservation.storage import JsonStore
from reservation.service import ReservationService


class JsonStoreTestCase(unittest.TestCase):
    """Base TestCase providing a per-test temporary JSON store."""

    def setUp(self):
        # Manage resource-allocating ops via ExitStack (satisfies pylint R1732)
        self._stack = ExitStack()
        self.addCleanup(self._stack.close)

        # Per-test temp dir
        self.tmp = self._stack.enter_context(tempfile.TemporaryDirectory())
        self.base = Path(self.tmp)

        # Json store + service
        self.store = JsonStore(self.base)
        self.svc = ReservationService(self.store)

        # Valid empty collections for each test
        (self.base / "hotels.json").write_text("[]", encoding="utf-8")
        (self.base / "customers.json").write_text("[]", encoding="utf-8")
        (self.base / "reservations.json").write_text("[]", encoding="utf-8")

    # Optional seed for suites that need a default hotel/customer
    def seed_baseline(self, *, hotel_id="H1", hotel_name="Hotel Azul", rooms=2,
                      customer_id="C1", customer_name="Benja",
                      customer_email="b@example.com") -> None:
        self.svc.create_hotel(hotel_id, hotel_name, rooms)
        self.svc.create_customer(customer_id, customer_name, customer_email)