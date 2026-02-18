"""Reservation tests for create/cancel flows and edge cases.

Covers happy path, out-of-range room numbers, duplicate ids, room occupancy
rules, and behavior when the underlying JSON file is malformed.
"""

# Pylint: keep tests lightweight—method names tell the story.
# We document at module/class level and disable missing function docstrings.
# This avoids docstring noise while preserving maintainability.
# pylint: disable=missing-function-docstring

import tempfile
import unittest
from pathlib import Path

from reservation.storage import JsonStore
from reservation.service import ReservationService


class ReservationTest(unittest.TestCase):
    """End-to-end reservation scenarios using a temporary JSON store."""

    def setUp(self):
        # Create a per-test temporary directory
        # and ensure cleanup is registered.
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        base = Path(self.tmp.name)
        self.store = JsonStore(base)
        self.svc = ReservationService(self.store)

        # Per-test data files (isolated)
        (base / "hotels.json").write_text("[]", encoding="utf-8")
        (base / "customers.json").write_text("[]", encoding="utf-8")
        (base / "reservations.json").write_text("[]", encoding="utf-8")

        # Common baseline data
        self.svc.create_hotel("H1", "Hotel Azul", rooms=2)
        self.svc.create_customer("C1", "Benja", "b@example.com")

    # Happy path
    def test_create_reservation_ok(self):
        rid = self.svc.create_reservation("R1", "H1", "C1", room_number=1)
        self.assertEqual("R1", rid)

    # Negative cases (≥ 5)
    def test_reservation_hotel_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R2", "H404", "C1", 1)

    def test_reservation_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R3", "H1", "C404", 1)

    def test_reservation_room_out_of_range_low_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R4", "H1", "C1", 0)

    def test_reservation_room_out_of_range_high_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R5", "H1", "C1", 3)  # rooms=2

    def test_reservation_id_duplicate_raises(self):
        self.svc.create_reservation("R6", "H1", "C1", 1)
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R6", "H1", "C1", 2)

    def test_reservation_room_already_taken_raises(self):
        self.svc.create_reservation("R7", "H1", "C1", 1)
        # Same room, same hotel, different reservation -> must fail
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R8", "H1", "C1", 1)

    def test_cancel_reservation_ok(self):
        self.svc.create_reservation("R9", "H1", "C1", 2)
        self.svc.cancel_reservation("R9")
        # Cancel twice should fail
        with self.assertRaises(ValueError):
            self.svc.cancel_reservation("R9")

    def test_cancel_unknown_reservation_raises(self):
        with self.assertRaises(ValueError):
            self.svc.cancel_reservation("RX")

    def test_corrupted_reservations_file_continue(self):
        base = Path(self.tmp.name)
        (base / "reservations.json").write_text(
            "{ BAD JSON ]", encoding="utf-8"
        )
        self.svc.create_reservation("R10", "H1", "C1", 2)
