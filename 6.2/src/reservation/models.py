from dataclasses import dataclass


@dataclass(frozen=True)
class Hotel:
    id: str
    name: str
    rooms: int


@dataclass(frozen=True)
class Customer:
    id: str
    name: str
    email: str


@dataclass(frozen=True)
class Reservation:
    id: str
    hotel_id: str
    customer_id: str
    room_number: int
