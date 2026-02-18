from __future__ import annotations
from typing import Dict, List, Optional

from .storage import JsonStore

class ReservationService:
    """Business operations for Hotel, Customer, Reservation."""

    HOTELS = "hotels.json"
    CUSTOMERS = "customers.json"
    RESERVATIONS = "reservations.json"

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    # ------- Hotels -------
    def create_hotel(self, hotel_id: str, name: str, rooms: int) -> None:
        if not hotel_id or not name or rooms <= 0:
            raise ValueError("Invalid hotel data")
        hotels = self.store.load(self.HOTELS)
        if any(h["id"] == hotel_id for h in hotels):
            raise ValueError(f"Hotel {hotel_id} already exists")
        hotels.append({"id": hotel_id, "name": name, "rooms": rooms})
        self.store.save(self.HOTELS, hotels)

    def get_hotel(self, hotel_id: str) -> Optional[Dict]:
        hotels = self.store.load(self.HOTELS)
        for h in hotels:
            if h["id"] == hotel_id:
                return h
        return None