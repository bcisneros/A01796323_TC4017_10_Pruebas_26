"""Reservation tests for create/cancel flows and edge cases.

Covers happy path, out-of-range room numbers, duplicate ids, room occupancy
rules, and behavior when the underlying JSON file is malformed.
"""

# Keep tests lightweight—method names tell the story.
# pylint: disable=missing-function-docstring
import unittest
from unittest.mock import MagicMock
from reservation.service import ReservationService


class ReservationTest(unittest.TestCase):
    """End-to-end reservation scenarios using a temporary JSON store."""

    def setUp(self):
        self.store, _ = self._store_with_maps(
            hotels=[{"id": "H1", "name": "Hotel Azul", "rooms": 2}],
            customers=[
                {"id": "C1", "name": "Benja", "email": "b@example.com"}
            ],
            reservations=[],
        )
        self.svc = ReservationService(self.store)

    def test_create_reservation_ok(self):
        rid = self.svc.create_reservation("R1", "H1", "C1", room_number=1)
        self.assertEqual("R1", rid)

        self.store.save.assert_called_once()
        args, _ = self.store.save.call_args
        self.assertEqual(ReservationService.RESERVATIONS, args[0])
        res = [
            {
                "id": "R1",
                "hotel_id": "H1",
                "customer_id": "C1",
                "room_number": 1,
                "status": "active"
            }
        ]
        self.assertEqual(res, args[1])

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
        self.store, _ = self._store_with_maps(
            hotels=[{"id": "H1", "name": "Hotel Azul", "rooms": 2}],
            customers=[
                {"id": "C1", "name": "Benja", "email": "b@example.com"},
                {"id": "C2", "name": "Juan", "email": "j@example.com"}
            ],
            reservations=[
                {
                    "id": "R9",
                    "hotel_id": "H1",
                    "customer_id": "C1",
                    "room_number": 1
                }
            ],
        )
        self.svc = ReservationService(self.store)
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R9", "H1", "C1", 2)

    def test_reservation_room_already_taken_raises(self):
        self.store, _ = self._store_with_maps(
            hotels=[{"id": "H1", "name": "Hotel Azul", "rooms": 2}],
            customers=[
                {"id": "C1", "name": "Benja", "email": "b@example.com"},
                {"id": "C2", "name": "Juan", "email": "j@example.com"}
            ],
            reservations=[
                {
                    "id": "R9",
                    "hotel_id": "H1",
                    "customer_id": "C1",
                    "room_number": 1
                }
            ],
        )
        self.svc = ReservationService(self.store)
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R10", "H1", "C2", 1)

    def test_cancel_reservation_ok(self):
        self.store, _ = self._store_with_maps(
            hotels=[{"id": "H1", "name": "Hotel Azul", "rooms": 2}],
            customers=[
                {"id": "C1", "name": "Benja", "email": "b@example.com"}
            ],
            reservations=[
                {
                    "id": "R9",
                    "hotel_id": "H1",
                    "customer_id": "C1",
                    "room_number": 2
                }
            ],
        )
        self.svc = ReservationService(self.store)
        self.svc.cancel_reservation("R9")
        self.store.save.assert_called_once()
        args, _ = self.store.save.call_args
        self.assertEqual(ReservationService.RESERVATIONS, args[0])
        self.assertEqual(
            [
                {
                    "id": "R9",
                    "hotel_id": "H1",
                    "customer_id": "C1",
                    "room_number": 2,
                    "status": "cancelled"
                }
            ],
            args[1]
        )

    def test_cancel_unknown_reservation_raises(self):
        with self.assertRaises(ValueError):
            self.svc.cancel_reservation("RX")

    @staticmethod
    def _store_with_maps(*, hotels=None, customers=None, reservations=None):
        store = MagicMock()
        # Respuestas por “catálogo” para load
        load_map = {
            ReservationService.HOTELS: hotels or [],
            ReservationService.CUSTOMERS: customers or [],
            ReservationService.RESERVATIONS: reservations or [],
        }
        store.load.side_effect = lambda name: load_map.get(name, [])
        return store, load_map
