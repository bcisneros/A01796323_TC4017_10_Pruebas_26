# tests/reservation_test.py
import tempfile
import unittest
from pathlib import Path

from reservation.storage import JsonStore
from reservation.service import ReservationService


class ReservationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.store = JsonStore(base)
        self.svc = ReservationService(self.store)

        # Archivos por prueba (aislados)
        (base / "hotels.json").write_text("[]", encoding="utf-8")
        (base / "customers.json").write_text("[]", encoding="utf-8")
        (base / "reservations.json").write_text("[]", encoding="utf-8")

        # Datos base para la mayoría de pruebas
        self.svc.create_hotel("H1", "Hotel Azul", rooms=2)
        self.svc.create_customer("C1", "Benja", "b@example.com")

    def tearDown(self):
        self.tmp.cleanup()

    # Happy path
    def test_create_reservation_ok(self):
        rid = self.svc.create_reservation("R1", "H1", "C1", room_number=1)
        self.assertEqual("R1", rid)

    # Negativos (≥ 5)
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
        # Mismo cuarto, mismo hotel, aunque sea otra reserva
        with self.assertRaises(ValueError):
            self.svc.create_reservation("R8", "H1", "C1", 1)

    def test_cancel_reservation_ok(self):
        self.svc.create_reservation("R9", "H1", "C1", 2)
        self.svc.cancel_reservation("R9")
        # Cancelar dos veces debe fallar:
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
