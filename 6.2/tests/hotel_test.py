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
