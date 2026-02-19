"""Reservation service layer.

This module defines the `ReservationService` class, which provides the
business operations for managing Hotels, Customers, and Reservations on
top of a simple JSON-backed persistence layer (`JsonStore`).

It covers:
- Hotel and Customer CRUD.
- Reservation create/cancel with business validations.
- Robustness to malformed JSON files (handled in `JsonStore.load`:
  it logs the error and continues with an empty list).
"""

from __future__ import annotations
from typing import Dict, List, Optional

from .models import Customer, Hotel, Reservation
from .storage import JsonStore


class ReservationService:
    """Business operations for Hotels, Customers, and Reservations.

    This service abstracts file access through `JsonStore` and centralizes
    rules such as:
    - Avoid creating duplicate entities by `id`.
    - Validate inputs (e.g., `rooms > 0`, emails contain '@', etc.).
    - Prevent double occupancy for a given (hotel_id, room_number).
    """

    HOTELS = "hotels.json"
    CUSTOMERS = "customers.json"
    RESERVATIONS = "reservations.json"

    def __init__(self, store: JsonStore) -> None:
        """Initialize the service with a `JsonStore` instance.

        Args:
            store: JSON store used to persist lists of dictionaries.
        """
        self.store = store

    # -------- Internal helpers --------
    def _load_hotels(self) -> List[Hotel]:
        """Return the list of hotels from the store."""
        rows: List[Dict] = self.store.load(self.HOTELS)
        return [Hotel.from_dict(r) for r in rows]

    def _save_hotels(self, hotels: List[Hotel]) -> None:
        rows = [h.to_dict() for h in hotels]
        self.store.save(self.HOTELS, rows)

    def _save_customers(self, customers: List[Customer]) -> None:
        rows = [c.to_dict() for c in customers]
        self.store.save(self.CUSTOMERS, rows)

    def _load_customers(self) -> List[Customer]:
        """Return the list of customers from the store."""
        rows: List[Dict] = self.store.load(self.CUSTOMERS)
        return [Customer.from_dict(r) for r in rows]

    def _load_reservations(self) -> List[Reservation]:
        """Return the list of reservations from the store."""
        rows: List[Dict] = self.store.load(self.RESERVATIONS)
        return [Reservation.from_dict(r) for r in rows]

    def _save_reservations(self, reservations: List[Reservation]) -> None:
        """Persist the given list of reservations to the store."""
        rows = [r.to_dict() for r in reservations]
        self.store.save(self.RESERVATIONS, rows)

    # -------- Hotels --------
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
        hotels = self._load_hotels()
        if any(h.id == hotel_id for h in hotels):
            raise ValueError(f"Hotel {hotel_id} already exists")
        hotel = Hotel(id=hotel_id, name=name, rooms=rooms)
        hotels.append(hotel)
        self._save_hotels(hotels)

    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """Return the hotel by id, or `None` if it does not exist.

        Args:
            hotel_id: Unique hotel identifier.

        Returns:
            dict | None: The hotel record if found, else None.
        """
        hotels = self._load_hotels()
        for h in hotels:
            if h.id == hotel_id:
                return h
        return None

    # -------- Customers --------
    def create_customer(self, customer_id: str, name: str, email: str) -> None:
        """Create a new customer if `customer_id` is unique and email is valid.

        Args:
            customer_id: Unique customer identifier.
            name: Customer name.
            email: Email address (must contain '@').

        Raises:
            ValueError: If data is invalid or the id already exists.
        """
        if not customer_id or not name or "@" not in email:
            raise ValueError("Invalid customer data")
        customers = self._load_customers()
        if any(c.id == customer_id for c in customers):
            raise ValueError(f"Customer {customer_id} already exists")
        customer = Customer(id=customer_id, name=name, email=email)
        customers.append(customer)
        self._save_customers(customers)

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Return the customer by id, or `None` if it does not exist.

        Args:
            customer_id: Unique customer identifier.

        Returns:
            Customer | None: The customer record if found, else None.
        """
        customers = self._load_customers()
        return next((c for c in customers if c.id == customer_id), None)

    def delete_customer(self, customer_id: str) -> None:
        """Delete a customer by id.

        Args:
            customer_id: Unique customer identifier.

        Raises:
            ValueError: If the customer does not exist.
        """
        customers = self._load_customers()
        new_customers = [c for c in customers if c.id != customer_id]
        if len(new_customers) == len(customers):
            raise ValueError("Customer not found")
        self._save_customers(new_customers)

    def delete_hotel(self, hotel_id: str) -> None:
        """Delete an hotel by id.

        Args:
            hotel_id: Unique hotel identifier.

        Raises:
            ValueError: If the hotel does not exist.
        """
        hotels = self._load_hotels()
        new_hotels = [h for h in hotels if h.id != hotel_id]
        if len(new_hotels) == len(hotels):
            raise ValueError("Hotel not found")
        self._save_hotels(new_hotels)

    def update_customer(self, customer_id: str, **fields) -> None:
        """Update fields on a customer record (e.g., `name`, `email`).

        Args:
            customer_id: Unique customer identifier.
            **fields: Arbitrary fields to update on the customer record.

        Raises:
            ValueError: If the customer does not exist.
        """
        customers = self._load_customers()
        idx = next(
            (i for i, c in enumerate(customers) if c.id == customer_id),
            -1
        )
        if idx < 0:
            raise ValueError("Customer not found")

        current = customers[idx]
        new_name = fields.get("name", current.name)
        new_email = fields.get("email", current.email)
        updated = Customer(id=current.id, name=new_name, email=new_email)

        customers[idx] = updated
        self._save_customers(customers)

    # -------- Reservations --------
    def create_reservation(
        self,
        reservation_id: str,
        hotel_id: str,
        customer_id: str,
        room_number: int,
    ) -> str:
        """Create a reservation if hotel/customer exist and the room is valid.

        Rules:
        - `room_number` must be between 1 and `hotel["rooms"]`.
        - `reservation_id` must be unique.
        - The (hotel_id, room_number) pair cannot be double-booked.

        Args:
            reservation_id: Unique reservation identifier.
            hotel_id: Hotel identifier.
            customer_id: Customer identifier.
            room_number: Room number (1..N).

        Returns:
            str: The created `reservation_id`.

        Raises:
            ValueError: If the hotel/customer is missing, room is invalid,
                        id is duplicated, or the room is already taken.
        """
        hotel = self.get_hotel(hotel_id)
        if hotel is None:
            raise ValueError("Hotel not found")
        customer = self.get_customer(customer_id)
        if customer is None:
            raise ValueError("Customer not found")
        if room_number <= 0 or room_number > hotel.rooms:
            raise ValueError("Invalid room number")

        reservations = self._load_reservations()
        if any(r.id == reservation_id for r in reservations):
            raise ValueError("Reservation id already exists")
        if any(
            r.hotel_id == hotel_id and r.room_number == int(room_number)
            for r in reservations
        ):
            raise ValueError("Room already taken")

        new_reservation = Reservation(id=reservation_id,
                                      hotel_id=hotel_id,
                                      customer_id=customer_id,
                                      room_number=room_number,
                                      status="active")
        reservations.append(new_reservation)
        self._save_reservations(reservations)
        return reservation_id

    def cancel_reservation(self, reservation_id: str) -> None:
        """Cancel a reservation by id.

        Args:
            reservation_id: Unique reservation identifier.

        Raises:
            ValueError: If the reservation does not exist.
        """
        reservations = self._load_reservations()
        idx = next(
            (i for i, c in enumerate(reservations) if c.id == reservation_id),
            -1
        )
        if idx < 0:
            raise ValueError("Reservation not found")

        current = reservations[idx]

        reservations[idx] = current.cancel()
        self._save_reservations(reservations)

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

    def update_hotel(self, hotel_id: str, **fields) -> None:
        """Update hotel attributes (e.g., name, rooms).

        Args:
            hotel_id: Unique hotel identifier.
            **fields: Fields to update (supported: name, rooms).

        Raises:
            ValueError: If the hotel does not exist or fields are invalid.
        """
        hotels = self._load_hotels()
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
        self._save_hotels(hotels)

    def display_customer_info(self, customer_id: str) -> str:
        """Return a human-friendly description of the customer.

        Args:
            customer_id: Unique customer identifier.

        Returns:
            str: Formatted description (id, name, email).

        Raises:
            ValueError: If the customer does not exist.
        """
        customer = self.get_customer(customer_id)
        if customer is None:
            raise ValueError("Customer not found")
        return str(customer)
