"""Reservation tests for create/cancel flows and edge cases.

Covers happy path, out-of-range room numbers, duplicate ids, room occupancy
rules, and behavior when the underlying JSON file is malformed.
"""

# Keep tests lightweight—method names tell the story.
# pylint: disable=missing-function-docstring

from pathlib import Path
from tests.support import JsonStoreTestCase


class ReservationTest(JsonStoreTestCase):
    """End-to-end reservation scenarios using a temporary JSON store."""

    def setUp(self):
        super().setUp()
        # Common baseline data (hotel+customer) for most tests
        self.seed_baseline(hotel_id="H1", hotel_name="Hotel Azul", rooms=2,
                           customer_id="C1", customer_name="Benja",
                           customer_email="b@example.com")

    def test_create_reservation_ok(self):
        rid = self.svc.create_reservation("R1", "H1", "C1", room_number=1)
        self.assertEqual("R1", rid)

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
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R8", "H1", "C1", 1)

    def test_cancel_reservation_ok(self):
        self.svc.create_reservation("R9", "H1", "C1", 2)
        self.svc.cancel_reservation("R9")
        with self.assertRaises(ValueError):
            self.svc.cancel_reservation("R9")

    def test_cancel_unknown_reservation_raises(self):
        with self.assertRaises(ValueError):
            self.svc.cancel_reservation("RX")

    def test_corrupted_reservations_file_continue(self):
        (self.base / "reservations.json").write_text("{ BAD JSON ]", encoding="utf-8")
        self.svc.create_reservation("R10", "H1", "C1", 2)
