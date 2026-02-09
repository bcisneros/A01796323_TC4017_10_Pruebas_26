# pylint: disable=invalid-name
"""
Compute sales totals from a product catalogue (JSON) and a sales file (JSON).

Usage:
    python computeSales.py products.json sales.json

This script prints a human-readable report to the console and writes the same
content to SalesResults.txt. It handles bad records gracefully (continues
processing and prints warnings), and reports elapsed time.
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


def load_catalogue(path: Path) -> Dict[str, float]:
    """Load product catalogue as a dict: title -> price."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Cannot read catalogue file {path}: {exc}")
        sys.exit(1)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in catalogue file {path}: {exc}")
        sys.exit(1)

    catalogue: Dict[str, float] = {}
    for item in data:
        # Validate expected keys and value types
        try:
            title = str(item["title"]).strip()
            price = float(item["price"])
        except (KeyError, TypeError, ValueError):
            print(f"WARNING: Invalid catalogue entry skipped: {item}")
            continue

        catalogue[title] = price

    return catalogue


def load_sales(path: Path) -> List[dict]:
    """Load sales as a list of dictionaries."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Cannot read sales file {path}: {exc}")
        sys.exit(1)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in sales file {path}: {exc}")
        sys.exit(1)

    return data


def compute_totals(
    catalogue: Dict[str, float],
    sales: List[dict],
) -> Tuple[List[dict], float]:
    """Compute per-line totals and a grand total from the inputs."""
    line_items: List[dict] = []
    total_sum = 0.0

    for idx, record in enumerate(sales):
        # Validate expected record fields
        try:
            product = str(record["Product"]).strip()
            qty = int(record["Quantity"])
        except (KeyError, TypeError, ValueError):
            print(
                "WARNING: Invalid record skipped at index "
                f"{idx}: {record}"
            )
            continue

        price = catalogue.get(product)
        if price is None:
            print(f"WARNING: Product not found in catalogue: {product}")
            continue

        line_total = price * qty
        total_sum += line_total
        line_items.append(
            {
                "product": product,
                "qty": qty,
                "price": price,
                "total": line_total
            }
        )

    return line_items, total_sum


def format_report(
    line_items: List[dict],
    total_sum: float,
    elapsed: float,
) -> str:
    """Return a human-readable multi-line report string."""
    lines = []
    lines.append("SALES RESULTS REPORT")
    lines.append("=" * 60)

    for item in line_items:
        lines.append(
            f"{item['product']:35}  "
            f"{item['qty']:3d} × ${item['price']:.2f}  "
            f"= ${item['total']:.2f}"
        )

    lines.append("=" * 60)
    lines.append(f"GRAND TOTAL: ${total_sum:.2f}")
    lines.append(f"Time elapsed: {elapsed:.3f} seconds")
    lines.append("=" * 60)

    return "\n".join(lines)


def main() -> None:
    """Entry point: parse arguments, run computation, write/print report."""
    if len(sys.argv) != 3:
        print("Usage: python computeSales.py products.json sales.json")
        sys.exit(1)

    products_path = Path(sys.argv[1])
    sales_path = Path(sys.argv[2])

    start = time.perf_counter()
    catalogue = load_catalogue(products_path)
    sales = load_sales(sales_path)
    line_items, total_sum = compute_totals(catalogue, sales)
    elapsed = time.perf_counter() - start

    report = format_report(line_items, total_sum, elapsed)
    print(report)

    try:
        Path("SalesResults.txt").write_text(report, encoding="utf-8")
        print("\nResults written to SalesResults.txt")
    except OSError as exc:
        print(f"ERROR: Could not write SalesResults.txt: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
