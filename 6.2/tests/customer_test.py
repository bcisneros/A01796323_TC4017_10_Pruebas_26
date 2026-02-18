"""Customer tests for CRUD flows and negative scenarios.

Covers create/get, duplicate id, invalid email, delete not found, and update
behaviors, using an isolated temporary JSON store per test.
"""

# Keep tests lightweight—method names tell the story.
# pylint: disable=missing-function-docstring

from tests.support import JsonStoreTestCase


class CustomerTest(JsonStoreTestCase):
    """Customer CRUD scenarios using a per-test temporary JSON store."""

    def setUp(self):
        super().setUp()
        # No baseline needed for the first test; others create explicitly.

    # Happy path: create and read back
    def test_create_and_get_customer(self):
        self.svc.create_customer("C1", "Benja", "b@example.com")
        c = self.svc.get_customer("C1")
        self.assertIsNotNone(c)
        self.assertEqual("Benja", c["name"])
        self.assertEqual("b@example.com", c["email"])

    # Negative 1: duplicate id
    def test_create_customer_duplicate_id_raises(self):
        self.svc.create_customer("C1", "User", "u@example.com")
        with self.assertRaises(ValueError):
            self.svc.create_customer("C1", "Other", "o@example.com")

    # Negative 2: invalid email
    def test_create_customer_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_customer("C2", "SinMail", "no-at-domain")

    # Negative 3: delete unknown
    def test_delete_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.delete_customer("C404")

    # Update existing record
    def test_update_customer_name(self):
        self.svc.create_customer("C3", "Nombre", "n@example.com")
        self.svc.update_customer("C3", name="Nuevo Nombre")
        c = self.svc.get_customer("C3")
        self.assertEqual("Nuevo Nombre", c["name"])

    # Negative 4: update unknown
    def test_update_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.update_customer("C404", name="X")
