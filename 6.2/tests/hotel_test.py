"""Hotel tests for create/get flows and negative scenarios.

Covers creation, retrieval, duplicate-id validation, invalid room counts,
and robustness when the underlying hotels JSON file is malformed.
"""

# Keep tests lightweight—method names tell the story.
# Document at module/class level; avoid noisy method docstrings.
# pylint: disable=missing-function-docstring

from tests.support import JsonStoreTestCase


class HotelTest(JsonStoreTestCase):
    """Hotel scenarios using a per-test temporary JSON store."""

    def test_create_and_get_hotel(self):
        self.svc.create_hotel(hotel_id="H1", name="Hotel Azul", rooms=3)
        hotel = self.svc.get_hotel("H1")
        self.assertEqual("Hotel Azul", hotel["name"])
        self.assertEqual(3, hotel["rooms"])

    # 1) Negative: duplicated id
    def test_create_hotel_duplicated_id_raises(self):
        self.svc.create_hotel("H1", "A", 1)
        with self.assertRaises(ValueError):
            self.svc.create_hotel("H1", "B", 2)

    # 2) Negative: rooms <= 0
    def test_create_hotel_invalid_rooms_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_hotel("H2", "X", 0)

    # 3) Negative: corrupted file -> should not crash; continue with []
    def test_load_corrupted_hotels_file_does_not_crash(self):
        (self.base / "hotels.json").write_text(
            "{ MALFORMED JSON ]", encoding="utf-8"
        )
        # Must continue and treat as empty list; create should work
        self.svc.create_hotel("H3", "Nuevo", 1)
        self.assertIsNotNone(self.svc.get_hotel("H3"))

    def test_create_hotel_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_hotel("", "X", 1)

    def test_create_hotel_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.svc.create_hotel("H2", "", 1)

    def test_get_hotel_returns_none_for_unknown_id(self):
        self.assertIsNone(self.svc.get_hotel("NOPE"))

    def test_load_returns_empty_when_hotels_file_absent(self):
        # Remove the file created by the base fixture to simulate
        # "missing file"
        (self.base / "hotels.json").unlink(missing_ok=True)

        rows = self.store.load("hotels.json")
        self.assertEqual([], rows)

    def test_display_hotel_info_returns_formatted_string(self):
        self.svc.create_hotel("HX", "Hotel X", 10)
        summary = self.svc.display_hotel_info("HX")
        self.assertEqual("Hotel HX: Hotel X (rooms=10)", summary)

    def test_display_hotel_info_unknown_hotel_raises(self):
        with self.assertRaises(ValueError):
            self.svc.display_hotel_info("NOPE")

    def test_update_hotel_name(self):
        # Arrange
        self.svc.create_hotel("HU1", "Old Name", 5)
        # Act
        self.svc.update_hotel("HU1", name="New Name")
        # Assert
        h = self.svc.get_hotel("HU1")
        self.assertEqual("New Name", h["name"])
        self.assertEqual(5, h["rooms"])  # unchanged

    def test_update_hotel_rooms(self):
        self.svc.create_hotel("HU2", "Hotel Rooms", 5)
        self.svc.update_hotel("HU2", rooms=8)
        h = self.svc.get_hotel("HU2")
        self.assertEqual(8, h["rooms"])

    def test_update_hotel_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.svc.update_hotel("NOPE", name="X")

    def test_update_hotel_invalid_rooms_raises(self):
        self.svc.create_hotel("HU3", "Hotel Invalid", 3)
        with self.assertRaises(ValueError):
            self.svc.update_hotel("HU3", rooms=0)

    def test_update_hotel_empty_name_raises(self):
        self.svc.create_hotel("HU4", "Will Rename", 3)
        with self.assertRaises(ValueError):
            self.svc.update_hotel("HU4", name="")
