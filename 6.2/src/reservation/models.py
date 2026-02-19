"""Domain models for the reservation system.

This module defines the immutable dataclasses used across the application:
- Hotel:     basic hotel metadata and total number of rooms.
- Customer:  basic customer identity and contact information.
- Reservation: a simple reservation record linking hotel, customer, and room.

These models are intentionally small and "frozen" (immutable) to improve
predictability in unit tests and to encourage explicit updates through the
service layer rather than in-place mutations.
"""

from dataclasses import dataclass, asdict


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

    @staticmethod
    def from_dict(data: dict) -> "Hotel":
        """Create a Hotel instance from a dictionary (store payload)."""
        return Hotel(
            id=data["id"],
            name=data["name"],
            rooms=data["rooms"],
        )

    def to_dict(self) -> dict:
        """Return the dictionary representation (for JSON persistence)."""
        return asdict(self)

    def __str__(self) -> str:
        """Human-friendly one-liner used to display hotel information."""
        return f"Hotel {self.id}: {self.name} (rooms={self.rooms})"


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

    @staticmethod
    def from_dict(data: dict) -> "Customer":
        """Create a Customer instance from a dictionary (store payload)."""
        return Customer(
            id=data["id"],
            name=data["name"],
            email=data["email"],
        )

    def to_dict(self) -> dict:
        """Return the dictionary representation (for JSON persistence)."""
        return asdict(self)

    def __str__(self) -> str:
        """Human-friendly one-liner used to display customer information."""
        return f"Customer {self.id}: {self.name} <{self.email}>"


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

    @staticmethod
    def from_dict(data: dict) -> "Reservation":
        """Create a Reservation instance from a dictionary (store payload)."""
        return Reservation(
            id=data["id"],
            hotel_id=data["hotel_id"],
            customer_id=data["customer_id"],
            room_number=data["room_number"]
        )

    def to_dict(self) -> dict:
        """Return the dictionary representation (for JSON persistence)."""
        return asdict(self)
