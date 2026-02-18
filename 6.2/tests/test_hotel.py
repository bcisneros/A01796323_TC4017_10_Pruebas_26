# tests/test_hotel.py
import json
import tempfile
import unittest
from pathlib import Path

from reservation.service import ReservationService
from reservation.storage import JsonStore

class TestHotel(unittest.TestCase):
    def setUp(self):
        # Carpeta temporal por test (cada test genera sus propios datos)
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.store = JsonStore(base)
        self.svc = ReservationService(self.store)
        # archivos vacíos válidos
        (base / "hotels.json").write_text("[]")
        (base / "customers.json").write_text("[]")
        (base / "reservations.json").write_text("[]")

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_and_get_hotel(self):
        self.svc.create_hotel(hotel_id="H1", name="Hotel Azul", rooms=3)
        hotel = self.svc.get_hotel("H1")
        self.assertEqual("Hotel Azul", hotel["name"])
        self.assertEqual(3, hotel["rooms"])

    # 1) Negativo: ID duplicado
    def test_create_hotel_duplicated_id_raises(self):
        self.svc.create_hotel("H1", "A", 1)
        with self.assertRaises(ValueError):
            self.svc.create_hotel("H1", "B", 2)

    # 2) Negativo: rooms <= 0
    def test_create_hotel_invalid_rooms_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_hotel("H2", "X", 0)

    # 3) Negativo: archivo corrupto -> no se cae; continúa con []
    def test_load_corrupted_hotels_file_does_not_crash(self):
        (Path(self.tmp.name) / "hotels.json").write_text("{ MALFORMED JSON ]")
        # Debe continuar y tratar como lista vacía; create debe funcionar
        self.svc.create_hotel("H3", "Nuevo", 1)
        self.assertIsNotNone(self.svc.get_hotel("H3"))