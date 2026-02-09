# pylint: disable=invalid-name
"""
Compute sales totals from a product catalogue (JSON) and a sales file (JSON).

Usage:
    python computeSales.py products.json sales.json [--no-messages]

This script prints a human-readable report to the console and writes the same
content to SalesResults.txt. It handles bad records gracefully (continues
processing and prints warnings), and reports elapsed time.

By default, non-fatal warnings and errors are included in the output.
Pass --no-messages to hide those sections.
"""

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class ReportData:
    """Container for the final report rendering."""
    line_items: List[dict]
    total_sum: float
    elapsed: float
    warnings: List[str]
    errors: List[str]
    include_messages: bool


def load_catalogue(path: Path, warnings: List[str]) -> Dict[str, float]:
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
            msg = f"Invalid catalogue entry skipped: {item}"
            warnings.append(msg)
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
    warnings: List[str],
    errors: List[str],
) -> Tuple[List[dict], float]:
    """Compute per-line totals and a grand total from the inputs.

    Non-fatal issues are appended to `warnings` or `errors`.
    """
    line_items: List[dict] = []
    total_sum = 0.0

    for idx, record in enumerate(sales):
        # Validate expected record fields
        try:
            product = str(record["Product"]).strip()
            qty = int(record["Quantity"])
        except (KeyError, TypeError, ValueError):
            warnings.append(
                "Invalid record skipped at index "
                f"{idx}: {record}"
            )
            continue

        price = catalogue.get(product)
        if price is None:
            errors.append(f"Product not found in catalogue: {product}")
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


def format_report(report: ReportData) -> str:
    """Return a human-readable multi-line report string."""
    lines: List[str] = []
    lines.append("SALES RESULTS REPORT")
    lines.append("=" * 60)

    for item in report.line_items:
        lines.append(
            f"{item['product']:35}  "
            f"{item['qty']:3d} × ${item['price']:.2f}  "
            f"= ${item['total']:.2f}"
        )

    lines.append("=" * 60)
    lines.append(f"GRAND TOTAL: ${report.total_sum:.2f}")
    lines.append(f"Time elapsed: {report.elapsed:.3f} seconds")
    lines.append("=" * 60)

    if report.include_messages:
        # WARNINGS section
        lines.append("WARNINGS")
        lines.append("-" * 60)
        if report.warnings:
            for msg in report.warnings:
                lines.append(f"- {msg}")
        else:
            lines.append("(none)")
        lines.append("")

        # ERRORS section
        lines.append("ERRORS")
        lines.append("-" * 60)
        if report.errors:
            for msg in report.errors:
                lines.append(f"- {msg}")
        else:
            lines.append("(none)")
        lines.append("=" * 60)

    return "\n".join(lines)


def parse_args(argv: List[str]) -> Tuple[Path, Path, bool]:
    """Parse simple argv: two positional files plus optional flag."""
    if len(argv) not in (3, 4):
        print(
            "Usage: python computeSales.py products.json sales.json "
            "[--no-messages]"
        )
        sys.exit(1)

    products_path = Path(argv[1])
    sales_path = Path(argv[2])
    include_messages = True

    if len(argv) == 4:
        if argv[3] == "--no-messages":
            include_messages = False
        else:
            print(
                "Unknown option: "
                f"{argv[3]}\nUse --no-messages or omit it."
            )
            sys.exit(1)

    return products_path, sales_path, include_messages


def main() -> None:
    """Entry point: parse args, run computation, write/print report."""
    products_path, sales_path, include_messages = parse_args(sys.argv)

    start = time.perf_counter()

    # Collect non-fatal messages to include in the report
    warnings: List[str] = []
    errors: List[str] = []

    catalogue = load_catalogue(products_path, warnings)
    sales = load_sales(sales_path)
    line_items, total_sum = compute_totals(catalogue, sales, warnings, errors)
    elapsed = time.perf_counter() - start

    report = ReportData(
        line_items=line_items,
        total_sum=total_sum,
        elapsed=elapsed,
        warnings=warnings,
        errors=errors,
        include_messages=include_messages,
    )

    output = format_report(report)
    print(output)

    try:
        Path("SalesResults.txt").write_text(output, encoding="utf-8")
        print("\nResults written to SalesResults.txt")
    except OSError as exc:
        print(f"ERROR: Could not write SalesResults.txt: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
