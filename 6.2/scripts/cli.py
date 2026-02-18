"""CLI application for the Reservation System.

- Presents a Spanish menu to manage Hotels, Customers, and Reservations.
- Uses the project's service layer (`reservation.service.ReservationService`)
  and JSON storage (`reservation.storage.JsonStore`).

UI strings are Spanish for end-user friendliness; code/docstrings in English
to keep linters happy and be consistent with earlier documentation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from reservation.service import ReservationService
from reservation.storage import JsonStore


def _input_nonempty(prompt: str) -> str:
    """Prompt until a non-empty string is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("⚠️  Entrada vacía, intenta de nuevo.")


def _input_int(prompt: str, min_value: Optional[int] = None) -> int:
    """Prompt for an integer; optionally enforce a minimum value."""
    while True:
        raw = input(prompt).strip()
        try:
            val = int(raw)
            if min_value is not None and val < min_value:
                print(f"⚠️  El valor debe ser ≥ {min_value}.")
                continue
            return val
        except ValueError:
            print("⚠️  Debes capturar un número entero.")


def bootstrap_data(base: Path) -> None:
    """Create initial JSON files with sample data if they don't exist.

    Files:
      - hotels.json       (2 hotels)
      - customers.json    (2 customers)
      - reservations.json (1 reservation)
    """
    hotels_path = base / 'hotels.json'
    customers_path = base / 'customers.json'
    reservations_path = base / 'reservations.json'

    if not hotels_path.exists():
        hotels_path.write_text(
            json_dumps_pretty([
                {"id": "H100", "name": "Hotel Centro", "rooms": 5},
                {"id": "H200", "name": "Hotel Norte", "rooms": 3},
            ]),
            encoding='utf-8',
        )
    if not customers_path.exists():
        customers_path.write_text(
            json_dumps_pretty([
                {
                    "id": "C100",
                    "name": "Alice Doe",
                    "email": "alice@example.com"
                },
                {
                    "id": "C200",
                    "name": "Bob Roe",
                    "email": "bob@example.com"
                },
            ]),
            encoding='utf-8',
        )
    if not reservations_path.exists():
        reservations_path.write_text(
            json_dumps_pretty([
                {
                    "id": "R100",
                    "hotel_id": "H100",
                    "customer_id": "C100",
                    "room_number": 1
                }
            ]),
            encoding='utf-8',
        )


def json_dumps_pretty(obj) -> str:
    import json as _json
    return _json.dumps(obj, ensure_ascii=False, indent=2)


def list_hotels(svc: ReservationService) -> None:
    hotels = svc._load_hotels()  # pylint: disable=protected-access
    if not hotels:
        print("(No hay hoteles)")
        return
    print("\nID     | Nombre         | Cuartos")
    print("-" * 38)
    for h in hotels:
        print(f"{h['id']:<6} | {h['name']:<14} | {h['rooms']}")


def list_customers(svc: ReservationService) -> None:
    customers = svc._load_customers()  # pylint: disable=protected-access
    if not customers:
        print("(No hay clientes)")
        return
    print("\nID     | Nombre         | Email")
    print("-" * 60)
    for c in customers:
        print(f"{c['id']:<6} | {c['name']:<14} | {c['email']}")


def list_reservations(svc: ReservationService) -> None:
    rows = svc._load_reservations()  # pylint: disable=protected-access
    if not rows:
        print("(No hay reservaciones)")
        return
    print("\nID     | Hotel  | Cliente | Habitación")
    print("-" * 42)
    for r in rows:
        id = f"{r['id']:<6}"
        hotel_id = f"{r['hotel_id']:<6}"
        customer_id = f"{r['customer_id']:<7}"
        room_number = f"{r['room_number']}"
        print(f"{id} | {hotel_id} | {customer_id} | {room_number}")


def menu_loop() -> None:
    """Interactive menu loop in Spanish."""
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)

    # Seed initial JSON if missing
    bootstrap_data(data_dir)

    store = JsonStore(data_dir)
    svc = ReservationService(store)

    actions = {
        '1': ('Crear hotel', action_create_hotel),
        '2': ('Mostrar hotel', action_display_hotel),
        '3': ('Modificar hotel', action_update_hotel),
        '4': ('Eliminar hotel', action_delete_hotel),
        '5': ('Listar hoteles', action_list_hotels),
        '6': ('Crear cliente', action_create_customer),
        '7': ('Mostrar cliente', action_display_customer),
        '8': ('Modificar cliente', action_update_customer),
        '9': ('Eliminar cliente', action_delete_customer),
        '10': ('Listar clientes', action_list_customers),
        '11': ('Crear reservación', action_create_reservation),
        '12': ('Cancelar reservación', action_cancel_reservation),
        '13': ('Listar reservaciones', action_list_reservations),
        '0': ('Salir', None),
    }

    while True:
        print("\n===== Sistema de Reservaciones =====")
        for key in [
            '1', '2', '3', '4', '5', '6',
            '7', '8', '9', '10', '11', '12', '13',
            '0'
        ]:
            title = actions[key][0]
            print(f"{key}. {title}")
        choice = input("Selecciona una opción: ").strip()
        if choice == '0':
            print("¡Hasta luego!")
            break
        action = actions.get(choice)
        if not action:
            print("⚠️  Opción inválida.")
            continue
        try:
            action[1](svc)
        except ValueError as exc:
            print(f"❌ Error: {exc}")
        except Exception as exc:  # pragma: no cover (defensive)
            print(f"❌ Error inesperado: {exc}")


# ---- Action handlers ------------------------------------------------------
def action_create_hotel(svc: ReservationService) -> None:
    hotel_id = _input_nonempty("Id del hotel: ")
    name = _input_nonempty("Nombre: ")
    rooms = _input_int("Número de cuartos: ", min_value=1)
    svc.create_hotel(hotel_id, name, rooms)
    print("✅ Hotel creado.")


def action_display_hotel(svc: ReservationService) -> None:
    hotel_id = _input_nonempty("Id del hotel: ")
    # Prefer service formatting if available; else compose from dict
    try:
        summary = svc.display_hotel_info(hotel_id)
    except AttributeError:
        # Fallback if display_hotel_info wasn't implemented
        h = svc.get_hotel(hotel_id)
        if h is None:
            raise ValueError("Hotel not found")
        summary = f"Hotel {h['id']}: {h['name']} (rooms={h['rooms']})"
    print(summary)


def action_update_hotel(svc: ReservationService) -> None:
    hotel_id = _input_nonempty("Id del hotel a modificar: ")
    print("Deja en blanco para mantener el valor actual.")
    name = input("Nuevo nombre: ").strip()
    rooms_raw = input("Nuevo número de cuartos: ").strip()
    fields = {}
    if name:
        fields['name'] = name
    if rooms_raw:
        try:
            rooms_val = int(rooms_raw)
        except ValueError:
            raise ValueError("rooms debe ser entero")
        fields['rooms'] = rooms_val
    if not fields:
        print("(Sin cambios)")
        return
    svc.update_hotel(hotel_id, **fields)  # type: ignore[attr-defined]
    print("✅ Hotel actualizado.")


def action_delete_hotel(svc: ReservationService) -> None:
    hotel_id = _input_nonempty("Id del hotel a eliminar: ")
    hotels = svc._load_hotels()  # pylint: disable=protected-access
    new_rows = [h for h in hotels if h['id'] != hotel_id]
    if len(new_rows) == len(hotels):
        raise ValueError("Hotel not found")
    svc.store.save(svc.HOTELS, new_rows)
    print("✅ Hotel eliminado.")


def action_list_hotels(svc: ReservationService) -> None:
    list_hotels(svc)


def action_create_customer(svc: ReservationService) -> None:
    customer_id = _input_nonempty("Id del cliente: ")
    name = _input_nonempty("Nombre: ")
    email = _input_nonempty("Email: ")
    svc.create_customer(customer_id, name, email)
    print("✅ Cliente creado.")


def action_display_customer(svc: ReservationService) -> None:
    customer_id = _input_nonempty("Id del cliente: ")
    try:
        summary = svc.display_customer_info(customer_id)
    except AttributeError:
        c = svc.get_customer(customer_id)
        if c is None:
            raise ValueError("Customer not found")
        summary = f"Customer {c['id']}: {c['name']} <{c['email']}>"
    print(summary)


def action_update_customer(svc: ReservationService) -> None:
    customer_id = _input_nonempty("Id del cliente a modificar: ")
    print("Deja en blanco para mantener el valor actual.")
    name = input("Nuevo nombre: ").strip()
    email = input("Nuevo email: ").strip()
    fields = {}
    if name:
        fields['name'] = name
    if email:
        fields['email'] = email
    if not fields:
        print("(Sin cambios)")
        return
    svc.update_customer(customer_id, **fields)
    print("✅ Cliente actualizado.")


def action_delete_customer(svc: ReservationService) -> None:
    customer_id = _input_nonempty("Id del cliente a eliminar: ")
    svc.delete_customer(customer_id)
    print("✅ Cliente eliminado.")


def action_list_customers(svc: ReservationService) -> None:
    list_customers(svc)


def action_create_reservation(svc: ReservationService) -> None:
    reservation_id = _input_nonempty("Id de reservación: ")
    hotel_id = _input_nonempty("Hotel id: ")
    customer_id = _input_nonempty("Cliente id: ")
    room_number = _input_int("Número de habitación: ", min_value=1)
    svc.create_reservation(reservation_id, hotel_id, customer_id, room_number)
    print("✅ Reservación creada.")


def action_cancel_reservation(svc: ReservationService) -> None:
    reservation_id = _input_nonempty("Id de reservación a cancelar: ")
    svc.cancel_reservation(reservation_id)
    print("✅ Reservación cancelada.")


def action_list_reservations(svc: ReservationService) -> None:
    list_reservations(svc)


if __name__ == '__main__':
    menu_loop()
