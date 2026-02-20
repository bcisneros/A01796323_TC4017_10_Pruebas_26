"""Hotel service layer.

This module defines the `HotelService` class, which provides the
business operations for managing Hotels on
top of a simple JSON-backed persistence layer (`JsonStore`).

It covers all Hotel CRUD operations.
"""
from __future__ import annotations
from typing import Dict, List, Optional

from .models import Hotel
from .storage import JsonStore


class HotelService:
    """
    Business operations for Hotels
    """

    HOTELS = "hotels.json"

    def __init__(
            self,
            store: JsonStore) -> None:
        """Initialize the service with a `JsonStore` instance.

        Args:
            store: JSON store used to persist lists of dictionaries.
        """
        self.store = store

    def load_hotels(self) -> List[Hotel]:
        """Return the list of hotels from the store."""
        rows: List[Dict] = self.store.load(self.HOTELS)
        return [Hotel.from_dict(r) for r in rows]

    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """Return the hotel by id, or `None` if it does not exist.

        Args:
            hotel_id: Unique hotel identifier.

        Returns:
            dict | None: The hotel record if found, else None.
        """
        hotels = self.load_hotels()
        for h in hotels:
            if h.id == hotel_id:
                return h
        return None

    def save_hotels(self, hotels: List[Hotel]) -> None:
        """Stores hotels in storage"""
        rows = [h.to_dict() for h in hotels]
        self.store.save(self.HOTELS, rows)

    def create_hotel(self, hotel_id: str, name: str, rooms: int) -> None:
        """Create a new hotel if `hotel_id` is unique and data is valid.

        Args:
            hotel_id: Unique hotel identifier.
            name: Hotel name.
            rooms: Total number of rooms (> 0).

        Raises:
            ValueError: If data is invalid or the id already exists.
        """
        if not hotel_id or not name or rooms <= 0:
            raise ValueError("Invalid hotel data")
        hotels = self.load_hotels()
        if any(h.id == hotel_id for h in hotels):
            raise ValueError(f"Hotel {hotel_id} already exists")
        hotel = Hotel(id=hotel_id, name=name, rooms=rooms)
        hotels.append(hotel)
        self.save_hotels(hotels)

    def update_hotel(self, hotel_id: str, **fields) -> None:
        """Update hotel attributes (e.g., name, rooms).

        Args:
            hotel_id: Unique hotel identifier.
            **fields: Fields to update (supported: name, rooms).

        Raises:
            ValueError: If the hotel does not exist or fields are invalid.
        """
        hotels = self.load_hotels()
        idx = next((i for i, h in enumerate(hotels) if h.id == hotel_id), -1)
        if idx < 0:
            raise ValueError("Hotel not found")

        current = hotels[idx]
        new_name = fields.get("name", current.name)
        new_rooms = fields.get("rooms", current.rooms)

        if not isinstance(new_name, str) or not new_name:
            raise ValueError("Invalid hotel name")
        if not isinstance(new_rooms, int) or new_rooms <= 0:
            raise ValueError("Invalid rooms value")

        hotels[idx] = Hotel(id=current.id, name=new_name, rooms=new_rooms)
        self.save_hotels(hotels)

    def delete_hotel(self, hotel_id: str) -> None:
        """Delete an hotel by id.

        Args:
            hotel_id: Unique hotel identifier.

        Raises:
            ValueError: If the hotel does not exist.
        """
        hotels = self.load_hotels()
        new_hotels = [h for h in hotels if h.id != hotel_id]
        if len(new_hotels) == len(hotels):
            raise ValueError("Hotel not found")
        self.save_hotels(new_hotels)

    def display_hotel_info(self, hotel_id: str) -> str:
        """Return a human-friendly description of the hotel.

        Args:
            hotel_id: Unique hotel identifier.

        Returns:
            str: Formatted description (id, name, rooms).

        Raises:
            ValueError: If the hotel does not exist.
        """
        hotel = self.get_hotel(hotel_id)
        if hotel is None:
            raise ValueError("Hotel not found")
        return str(hotel)
