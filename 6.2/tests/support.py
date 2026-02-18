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

    def seed_baseline(  # pylint: disable=too-many-arguments
        self,
        *,
        hotel_id: str = "H1",
        hotel_name: str = "Hotel Azul",
        rooms: int = 2,
        customer_id: str = "C1",
        customer_name: str = "Benja",
        customer_email: str = "b@example.com",
    ) -> None:
        """Seed a default hotel and customer commonly used by reservation tests.

        Args:
            hotel_id: Hotel identifier (default: 'H1').
            hotel_name: Hotel name (default: 'Hotel Azul').
            rooms: Total hotel rooms (default: 2).
            customer_id: Customer identifier (default: 'C1').
            customer_name: Customer's name (default: 'Benja').
            customer_email: Customer's email (default: 'b@example.com').
        """
        self.svc.create_hotel(hotel_id, hotel_name, rooms)
        self.svc.create_customer(customer_id, customer_name, customer_email)
