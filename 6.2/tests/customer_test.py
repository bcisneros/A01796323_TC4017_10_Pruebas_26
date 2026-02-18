# tests/customer_test.py
import tempfile
import unittest
from pathlib import Path

from reservation.storage import JsonStore
from reservation.service import ReservationService


class CustomerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.store = JsonStore(base)
        self.svc = ReservationService(self.store)

        # Datos aislados por prueba
        (base / "hotels.json").write_text("[]", encoding="utf-8")
        (base / "customers.json").write_text("[]", encoding="utf-8")
        (base / "reservations.json").write_text("[]", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    # Happy path: crear y consultar
    def test_create_and_get_customer(self):
        self.svc.create_customer("C1", "Benja", "b@example.com")
        c = self.svc.get_customer("C1")
        self.assertIsNotNone(c)
        self.assertEqual("Benja", c["name"])
        self.assertEqual("b@example.com", c["email"])

    # Negativo 1: ID duplicado
    def test_create_customer_duplicate_id_raises(self):
        self.svc.create_customer("C1", "User", "u@example.com")
        with self.assertRaises(ValueError):
            self.svc.create_customer("C1", "Other", "o@example.com")

    # Negativo 2: email inválido
    def test_create_customer_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_customer("C2", "SinMail", "no-at-domain")

    # Negativo 3: borrar inexistente
    def test_delete_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.delete_customer("C404")

    # Actualizar datos existentes
    def test_update_customer_name(self):
        self.svc.create_customer("C3", "Nombre", "n@example.com")
        self.svc.update_customer("C3", name="Nuevo Nombre")
        c = self.svc.get_customer("C3")
        self.assertEqual("Nuevo Nombre", c["name"])

    # Negativo 4: actualizar inexistente
    def test_update_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.update_customer("C404", name="X")
