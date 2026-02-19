"""Hotel tests for create/get flows and negative scenarios.

Covers creation, retrieval, duplicate-id validation, invalid room counts,
and robustness when the underlying hotels JSON file is malformed.
"""

# Keep tests lightweight—method names tell the story.
# Document at module/class level; avoid noisy method docstrings.
# pylint: disable=missing-function-docstring
import copy
import unittest
from unittest.mock import MagicMock

from reservation.service import ReservationService


class HotelTest(unittest.TestCase):
    """Hotel scenarios using a per-test temporary JSON store."""

    def setUp(self):
        # Mocked store for every test
        self.store = MagicMock()
        self.svc = ReservationService(self.store)

    def test_create_hotel_writes_expected_row(self):
        # Arrange
        self.store.load.return_value = []  # no hotels yet
        # Act
        self.svc.create_hotel("H1", "Hotel Azul", 3)
        # Assert
        self.store.load.assert_called_once_with(self.svc.HOTELS)
        self.store.save.assert_called_once()
        args, _ = self.store.save.call_args
        self.assertEqual(self.svc.HOTELS, args[0])
        data = [{"id": "H1", "name": "Hotel Azul", "rooms": 3}]
        self.assertEqual(data, args[1])

    def test_create_hotel_with_valid_rooms(self):
        self.store.load.return_value = []

        self.svc.create_hotel("H1", "Hotel Azul", 1)

        self.store.save.assert_called_once()
        args, _ = self.store.save.call_args
        self.assertEqual(self.svc.HOTELS, args[0])
        self.assertEqual(1, args[1][0]["rooms"])

    # 1) Negative: duplicated id
    def test_create_hotel_duplicated_id_raises(self):
        self.store.load.return_value = [{"id": "H1", "name": "A", "rooms": 1}]
        with self.assertRaises(ValueError):
            self.svc.create_hotel("H1", "B", 2)
        self.store.save.assert_not_called()

    # 2) Negative: rooms <= 0
    def test_create_hotel_invalid_rooms_raises(self):
        # rooms <= 0 should fail before touching the store
        with self.assertRaises(ValueError):
            self.svc.create_hotel("HX", "X", 0)
        self.store.load.assert_not_called()
        self.store.save.assert_not_called()

    def test_create_hotel_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_hotel("", "X", 1)
        self.store.load.assert_not_called()
        self.store.save.assert_not_called()

    def test_create_hotel_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_hotel("H2", "", 1)
        self.store.load.assert_not_called()
        self.store.save.assert_not_called()

    def test_get_hotel_existing_id_returns_hotel_data(self):
        data = [
            {"id": "H1", "name": "First Hotel", "rooms": 1},
            {"id": "H2", "name": "Second Hotel", "rooms": 3},
            {"id": "H3", "name": "Third Hotel", "rooms": 9}
        ]
        self.store.load.return_value = data
        hotel = self.svc.get_hotel("H2")

        self.assertEqual(
            {"id": "H2", "name": "Second Hotel", "rooms": 3},
            hotel.to_dict()
        )

    def test_get_hotel_returns_none_for_unknown_id(self):
        data = [{"id": "H2", "name": "Other", "rooms": 1}]
        self.store.load.return_value = data
        self.assertIsNone(self.svc.get_hotel("NOPE"))

    def test_display_hotel_info_returns_formatted_string(self):
        data = [{"id": "HX", "name": "Hotel X", "rooms": 10}]
        self.store.load.return_value = data
        summary = self.svc.display_hotel_info("HX")
        self.assertEqual("Hotel HX: Hotel X (rooms=10)", summary)

    def test_display_hotel_info_unknown_raises(self):
        data = [{"id": "HX", "name": "Hotel X", "rooms": 10}]
        self.store.load.return_value = data
        with self.assertRaises(ValueError):
            _ = self.svc.display_hotel_info("NOPE")

    def test_update_hotel_name(self):
        initial = [{"id": "H1", "name": "Old", "rooms": 3}]
        self.store.load.return_value = copy.deepcopy(initial)

        self.svc.update_hotel("H1", name="New")
        self.store.load.assert_called_once_with(self.svc.HOTELS)
        self.store.save.assert_called_once()
        args, _ = self.store.save.call_args
        self.assertEqual(self.svc.HOTELS, args[0])
        self.assertEqual([{"id": "H1", "name": "New", "rooms": 3}], args[1])

    def test_update_hotel_rooms(self):
        self.store.load.return_value = [{"id": "H1", "name": "X", "rooms": 3}]
        self.svc.update_hotel("H1", rooms=8)
        args, _ = self.store.save.call_args
        self.assertEqual([{"id": "H1", "name": "X", "rooms": 8}], args[1])

    def test_update_hotel_not_found_raises(self):
        self.store.load.return_value = [{"id": "HX", "name": "X", "rooms": 1}]
        with self.assertRaises(ValueError):
            self.svc.update_hotel("NOPE", name="Y")
        self.store.save.assert_not_called()

    def test_update_hotel_invalid_rooms_raises(self):
        self.store.load.return_value = [{"id": "H1", "name": "X", "rooms": 3}]
        with self.assertRaises(ValueError):
            self.svc.update_hotel("H1", rooms=0)
        self.store.save.assert_not_called()

    def test_update_hotel_empty_name_raises(self):
        self.store.load.return_value = [{"id": "H1", "name": "X", "rooms": 3}]
        with self.assertRaises(ValueError):
            self.svc.update_hotel("H1", name="")
        self.store.save.assert_not_called()
