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
    # -------- Helpers internos --------
    def _load_hotels(self) -> List[Dict]:
        return self.store.load(self.HOTELS)

    def _load_customers(self) -> List[Dict]:
        return self.store.load(self.CUSTOMERS)

    def _load_reservations(self) -> List[Dict]:
        return self.store.load(self.RESERVATIONS)

    def _save_reservations(self, rows: List[Dict]) -> None:
        self.store.save(self.RESERVATIONS, rows)
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
    
    # -------- Customers --------
    def create_customer(self, customer_id: str, name: str, email: str) -> None:
        if not customer_id or not name or "@" not in email:
            raise ValueError("Invalid customer data")
        customers = self.store.load(self.CUSTOMERS)
        if any(c["id"] == customer_id for c in customers):
            raise ValueError(f"Customer {customer_id} already exists")
        customers.append({"id": customer_id, "name": name, "email": email})
        self.store.save(self.CUSTOMERS, customers)

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        customers = self.store.load(self.CUSTOMERS)
        return next((c for c in customers if c["id"] == customer_id), None)

    def delete_customer(self, customer_id: str) -> None:
        customers = self.store.load(self.CUSTOMERS)
        new_customers = [c for c in customers if c["id"] != customer_id]
        if len(new_customers) == len(customers):
            raise ValueError("Customer not found")
        self.store.save(self.CUSTOMERS, new_customers)

    def update_customer(self, customer_id: str, **fields) -> None:
        customers = self.store.load(self.CUSTOMERS)
        found = False
        for c in customers:
            if c["id"] == customer_id:
                c.update(fields)
                found = True
        if not found:
            raise ValueError("Customer not found")
        self.store.save(self.CUSTOMERS, customers)




    # -------- API pública: Reservations --------
    def create_reservation(self, reservation_id: str, hotel_id: str,
                           customer_id: str, room_number: int) -> str:
        hotel = self.get_hotel(hotel_id)
        if hotel is None:
            raise ValueError("Hotel not found")
        customer = self.get_customer(customer_id)
        if customer is None:
            raise ValueError("Customer not found")
        if room_number <= 0 or room_number > hotel["rooms"]:
            raise ValueError("Invalid room number")

        reservations = self._load_reservations()
        if any(r["id"] == reservation_id for r in reservations):
            raise ValueError("Reservation id already exists")

        # regla simple: un cuarto por hotel no puede tener 2 reservas simultáneas
        if any(r["hotel_id"] == hotel_id and r["room_number"] == room_number
               for r in reservations):
            raise ValueError("Room already taken")

        reservations.append({
            "id": reservation_id,
            "hotel_id": hotel_id,
            "customer_id": customer_id,
            "room_number": room_number
        })
        self._save_reservations(reservations)
        return reservation_id

    def cancel_reservation(self, reservation_id: str) -> None:
        reservations = self._load_reservations()
        new_rows = [r for r in reservations if r["id"] != reservation_id]
        if len(new_rows) == len(reservations):
            raise ValueError("Reservation not found")
        self._save_reservations(new_rows)