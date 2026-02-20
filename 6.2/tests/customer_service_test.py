"""Customer tests for CRUD flows and negative scenarios.

Covers create/get, duplicate id, invalid email, delete not found, and update
behaviors, using an isolated mock JSON store per test.
"""

# Keep tests lightweight—method names tell the story.
# pylint: disable=missing-function-docstring
import unittest
from unittest.mock import MagicMock

from reservation.customer_service import CustomerService


class CustomerTest(unittest.TestCase):
    """Customer CRUD scenarios using a per-test mock JSON store."""

    def setUp(self):
        # Mocked store for every test
        self.store = MagicMock()
        self.svc = CustomerService(self.store)

    # --- Create Customers ---
    # Happy path: create and read back
    def test_create_customer_writes_to_storage(self):
        # Arrange
        self.store.load.return_value = []
        # Act
        self.svc.create_customer("C1", "Benja", "b@example.com")
        # Assert
        self.store.load.assert_called_once_with(self.svc.CUSTOMERS)
        data = [{"id": "C1", "name": "Benja", "email": "b@example.com"}]
        self._assert_save(data)

    # Negative 1: duplicate id
    def test_create_customer_duplicate_id_raises(self):
        # Arrange
        data = [{"id": "C1", "name": "John", "email": "john@test.com"}]
        self.store.load.return_value = data
        # Act
        with self.assertRaises(ValueError):
            self.svc.create_customer("C1", "Other", "o@example.com")
        # Assert
        self.store.save.assert_not_called()

    # Negative 2: invalid email
    def test_create_customer_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_customer("C2", "SinMail", "no-at-domain")

    def test_create_customer_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_customer("", "A", "a@example.com")

    def test_create_customer_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_customer("C2", "", "a@example.com")

    # --- Delete Customers ---
    def test_delete_customer_ok(self):
        # Arrange
        data = [{"id": "C10", "name": "X", "email": "x@x.com"}]
        self.store.load.return_value = data
        # Act
        self.svc.delete_customer("C10")
        # Assert
        self._assert_save([])

    # Negative 3: delete unknown
    def test_delete_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.delete_customer("C404")

    # --- Update Customers ---
    # Update existing record
    def test_update_customer_name(self):
        # Arrange
        data = [{"id": "C3", "name": "John", "email": "john@test.com"}]
        self.store.load.return_value = data
        # Act
        self.svc.update_customer("C3", name="Juan")
        # Assert
        new_data = [{"id": "C3", "name": "Juan", "email": "john@test.com"}]
        self._assert_save(new_data)

    # Negative 4: update unknown
    def test_update_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.update_customer("C404", name="X")

    # --- Get Customer ---

    def test_get_customer_existing_customer(self):
        data = [{"id": "C4", "name": "Benja", "email": "benja@test.com"}]
        self.store.load.return_value = data

        customer = self.svc.get_customer("C4")
        self.assertIsNotNone(customer)
        self.assertEqual("Benja", customer.name)
        self.assertEqual("benja@test.com", customer.email)

    def test_get_customer_returns_none_for_unknown_id(self):
        self.assertIsNone(self.svc.get_customer("NOPE"))

    # --- Display Customer Info ---

    def test_display_customer_info_returns_formatted_string(self):
        # Arrange
        data = [{"id": "CX", "name": "John Doe", "email": "john@example.com"}]
        self._load_returns(data)
        # Act
        summary = self.svc.display_customer_info("CX")
        # Assert
        self.assertEqual("Customer CX: John Doe <john@example.com>", summary)

    def test_display_customer_info_unknown_customer_raises(self):
        with self.assertRaises(ValueError):
            self.svc.display_customer_info("NOPE")

    def _assert_save(self, data):
        self.store.save.assert_called_once()
        args, _ = self.store.save.call_args
        self.assertEqual(self.svc.CUSTOMERS, args[0])
        self.assertEqual(data, args[1])

    def _load_returns(self, data):
        self.store.load.return_value = data
