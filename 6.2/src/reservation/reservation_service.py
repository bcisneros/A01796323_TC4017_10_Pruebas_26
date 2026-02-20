"""Reservation service layer.

This module defines the `ReservationService` class, which provides the
business operations for managing Reservations on
top of a simple JSON-backed persistence layer (`JsonStore`).

It covers:
- Reservation create/cancel with business validations.
"""

from __future__ import annotations
from typing import Callable, Dict, List, Optional
from datetime import datetime

from .hotel_service import HotelService
from .customer_service import CustomerService
from .models import Reservation
from .storage import JsonStore


class ReservationService:
    """Business operations for Reservations.

    This service abstracts file access through `JsonStore` and centralizes
    rules such as:
    - Avoid creating duplicate entities by `id`.
    - Prevent double occupancy for a given (hotel_id, room_number).
    """

    RESERVATIONS = "reservations.json"

    def __init__(
            self,
            store: JsonStore,
            now: Optional[Callable[[], str]] = None) -> None:
        """Initialize the service with a `JsonStore` instance.

        Args:
            store: JSON store used to persist lists of dictionaries.
        """
        self.store = store
        self.now = now or (lambda: datetime.now().astimezone().isoformat())
        self.hotel_service = HotelService(store)
        self.customer_service = CustomerService(store)

    def _load_reservations(self) -> List[Reservation]:
        """Return the list of reservations from the store."""
        rows: List[Dict] = self.store.load(self.RESERVATIONS)
        return [Reservation.from_dict(r) for r in rows]

    def _save_reservations(self, reservations: List[Reservation]) -> None:
        """Persist the given list of reservations to the store."""
        rows = [r.to_dict() for r in reservations]
        self.store.save(self.RESERVATIONS, rows)

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
        hotel = self.hotel_service.get_hotel(hotel_id)
        if hotel is None:
            raise ValueError("Hotel not found")
        customer = self.customer_service.get_customer(customer_id)
        if customer is None:
            raise ValueError("Customer not found")
        if room_number <= 0 or room_number > hotel.rooms:
            raise ValueError("Invalid room number")

        reservations = self._load_reservations()
        if any(r.id == reservation_id for r in reservations):
            raise ValueError("Reservation id already exists")
        if any(
            r.hotel_id == hotel_id
            and r.room_number == int(room_number)
            and r.status == "active"
            for r in reservations
        ):
            raise ValueError("Room already taken")

        new_reservation = Reservation(id=reservation_id,
                                      created_at=self.now(),
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
