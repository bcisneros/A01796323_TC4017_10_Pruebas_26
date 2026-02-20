"""Customer service layer.

This module defines the `CustomerService` class, which provides the
business operations for managing Customers on
top of a simple JSON-backed persistence layer (`JsonStore`).

It covers all Customer CRUD operations.
"""

from __future__ import annotations
from typing import Dict, List, Optional

from .models import Customer
from .storage import JsonStore


class CustomerService:
    """
    Business operations for Customers
    """

    CUSTOMERS = "customers.json"

    def save_customers(self, customers: List[Customer]) -> None:
        """Stores list of customers"""
        rows = [c.to_dict() for c in customers]
        self.store.save(self.CUSTOMERS, rows)

    def load_customers(self) -> List[Customer]:
        """Return the list of customers from the store."""
        rows: List[Dict] = self.store.load(self.CUSTOMERS)
        return [Customer.from_dict(r) for r in rows]

    def __init__(self, store: JsonStore) -> None:
        """Initialize the service with a `JsonStore` instance.

        Args:
            store: JSON store used to persist lists of dictionaries.
        """
        self.store = store

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
        customers = self.load_customers()
        if any(c.id == customer_id for c in customers):
            raise ValueError(f"Customer {customer_id} already exists")
        customer = Customer(id=customer_id, name=name, email=email)
        customers.append(customer)
        self.save_customers(customers)

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Return the customer by id, or `None` if it does not exist.

        Args:
            customer_id: Unique customer identifier.

        Returns:
            Customer | None: The customer record if found, else None.
        """
        customers = self.load_customers()
        return next((c for c in customers if c.id == customer_id), None)

    def delete_customer(self, customer_id: str) -> None:
        """Delete a customer by id.

        Args:
            customer_id: Unique customer identifier.

        Raises:
            ValueError: If the customer does not exist.
        """
        customers = self.load_customers()
        new_customers = [c for c in customers if c.id != customer_id]
        if len(new_customers) == len(customers):
            raise ValueError("Customer not found")
        self.save_customers(new_customers)

    def update_customer(self, customer_id: str, **fields) -> None:
        """Update fields on a customer record (e.g., `name`, `email`).

        Args:
            customer_id: Unique customer identifier.
            **fields: Arbitrary fields to update on the customer record.

        Raises:
            ValueError: If the customer does not exist.
        """
        customers = self.load_customers()
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
        self.save_customers(customers)

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
