"""Domain models for the reservation system.

This module defines the immutable dataclasses used across the application:
- Hotel:     basic hotel metadata and total number of rooms.
- Customer:  basic customer identity and contact information.
- Reservation: a simple reservation record linking hotel, customer, and room.

These models are intentionally small and "frozen" (immutable) to improve
predictability in unit tests and to encourage explicit updates through the
service layer rather than in-place mutations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Hotel:
    """Represents a hotel with a unique id, display name, and room capacity.

    Attributes:
        id: Unique hotel identifier.
        name: Human-readable hotel name.
        rooms: Total number of rooms available in this hotel (must be > 0).
    """
    id: str
    name: str
    rooms: int


@dataclass(frozen=True)
class Customer:
    """Represents a customer with identity and contact information.

    Attributes:
        id: Unique customer identifier.
        name: Customer's full name.
        email: Customer's email address.
    """
    id: str
    name: str
    email: str


@dataclass(frozen=True)
class Reservation:
    """Represents a room reservation linking a customer to a hotel room.

    Attributes:
        id: Unique reservation identifier.
        hotel_id: Identifier of the hotel being reserved.
        customer_id: Identifier of the customer who made the reservation.
        room_number: Room number within the specified hotel.
    """
    id: str
    hotel_id: str
    customer_id: str
    room_number: int
