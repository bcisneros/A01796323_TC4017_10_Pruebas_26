# pylint: disable=invalid-name
"""
Compute sales totals from a product catalogue (JSON) and a sales file (JSON).

Usage:
    python computeSales.py products.json sales.json [--no-messages]
                                                  [--outdir PATH]

This script prints a human-readable report to the console and writes the same
content to SalesResults.txt. It handles bad records gracefully (continues
processing and prints warnings), and reports elapsed time.

By default, non-fatal warnings and errors are included in the output.
Pass --no-messages to hide those sections.

Use --outdir PATH to choose the output directory for SalesResults.txt.
If not provided, the current directory is used.

Layout:
- Group by SALE_Date, then by SALE_ID.
- Date line shows the total for that date (right-aligned).
- Sale header shows sale total (right-aligned).
- Lines within a sale are numbered and show Product, Qty, Price, Subtotal.
- Grand Total at the end (right-aligned).
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

    line_items schema (per line):
        {
            "date": str,
            "sale_id": int,
            "product": str,
            "qty": int,
            "price": float,
            "subtotal": float
        }

    Non-fatal issues are appended to `warnings` or `errors`.
    """
    line_items: List[dict] = []
    total_sum = 0.0

    for idx, record in enumerate(sales):
        # Validate expected record fields
        try:
            sale_date = str(record["SALE_Date"]).strip()
            sale_id = int(record["SALE_ID"])
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

        subtotal = price * qty
        total_sum += subtotal
        line_items.append(
            {
                "date": sale_date,
                "sale_id": sale_id,
                "product": product,
                "qty": qty,
                "price": price,
                "subtotal": subtotal,
            }
        )

    return line_items, total_sum


def _group_by_date_then_sale(
        line_items: List[dict]) -> Dict[str, Dict[int, List[dict]]]:
    """Return nested grouping: date -> sale_id -> list of items."""
    grouped: Dict[str, Dict[int, List[dict]]] = {}
    for item in line_items:
        date = item["date"]
        sale_id = item["sale_id"]
        grouped.setdefault(date, {}).setdefault(sale_id, []).append(item)
    return grouped


def format_report(report: ReportData) -> str:
    """
    Return the report string grouped by date then sale, with aligned totals.
    """
    W = 72  # max content width for neat wrapping
    lines: List[str] = []
    lines.append("SALES RESULTS REPORT")
    lines.append("=" * W)

    # Group items
    grouped = _group_by_date_then_sale(report.line_items)

    # Sort dates ascending as strings; modify if you need custom sort
    for date in sorted(grouped.keys()):
        # Compute total for the whole date
        date_total = 0.0
        for sale_items in grouped[date].values():
            date_total += sum(li["subtotal"] for li in sale_items)

        date_total_str = f"${date_total:,.2f}"
        # Date header with right-aligned total
        date_hdr = f"{date}"
        pad = max(1, W - len(date_hdr) - len(date_total_str))
        lines.append(f"{date_hdr}{' ' * pad}{date_total_str}")

        # Per-sale sections for this date
        for sale_id in sorted(grouped[date].keys()):
            items = grouped[date][sale_id]
            sale_total = sum(li["subtotal"] for li in items)
            sale_total_str = f"${sale_total:,.2f}"

            sale_hdr = f"  SALE_ID: {sale_id}"
            pad2 = max(1, W - len(sale_hdr) - len(sale_total_str))
            lines.append(f"{sale_hdr}{' ' * pad2}{sale_total_str}")

            # Table header for the sale
            lines.append(
                f"{'':2}{'#':>3}  {'PRODUCT':35} "
                f"{'QTY':>5} {'PRICE':>10} {'SUBTOTAL':>12}"
            )

            # Table rows
            for idx, li in enumerate(items, start=1):
                prod = li["product"]
                qty = li["qty"]
                price = li["price"]
                price_str = f"${price:.2f}"
                sub = li["subtotal"]
                sub_str = f"${sub:.2f}"
                lines.append(
                    f"{'':2}{idx:>3}  {prod:35.35} "
                    f"{qty:>5d} {price_str:>10} {sub_str:>12}"
                )

            # Spacer between sales
            lines.append("-" * W)

        # Blank line between dates
        lines.append("")

    # Grand total + elapsed
    grand_str = f"${report.total_sum:,.2f}"
    lines.append("=" * W)
    # Right-align the grand total label/amount
    label = "GRAND TOTAL:"
    pad_gt = max(1, W - len(label) - len(grand_str))
    lines.append(f"{label}{' ' * pad_gt}{grand_str}")
    lines.append(f"Time elapsed: {report.elapsed:.3f} seconds")
    lines.append("=" * W)

    if report.include_messages:
        # WARNINGS
        lines.append("WARNINGS")
        lines.append("-" * W)
        if report.warnings:
            for msg in report.warnings:
                lines.append(f"- {msg}")
        else:
            lines.append("(none)")
        lines.append("")

        # ERRORS
        lines.append("ERRORS")
        lines.append("-" * W)
        if report.errors:
            for msg in report.errors:
                lines.append(f"- {msg}")
        else:
            lines.append("(none)")
        lines.append("=" * W)

    return "\n".join(lines)


def parse_args(argv: List[str]) -> Tuple[Path, Path, bool, Path]:
    """Parse args: two positional files + optional flags in any order.

    Supported options:
      --no-messages          Hide WARNINGS and ERRORS sections
      --outdir PATH          Output directory for SalesResults.txt
    """
    if len(argv) < 3:
        print(
            "Usage: python computeSales.py products.json sales.json "
            "[--no-messages] [--outdir PATH]"
        )
        sys.exit(1)

    products_path = Path(argv[1])
    sales_path = Path(argv[2])

    include_messages = True
    outdir = Path(".")

    idx = 3
    while idx < len(argv):
        token = argv[idx]
        if token == "--no-messages":
            include_messages = False
            idx += 1
            continue
        if token == "--outdir":
            if idx + 1 >= len(argv):
                print("ERROR: --outdir requires a PATH argument")
                sys.exit(1)
            outdir = Path(argv[idx + 1])
            idx += 2
            continue
        print(f"Unknown option: {token}")
        print("Use: [--no-messages] [--outdir PATH] or omit them.")
        sys.exit(1)

    return products_path, sales_path, include_messages, outdir


def run(
        products_path: Path,
        sales_path: Path,
        include_messages: bool) -> ReportData:
    """End-to-end compute: load inputs, compute totals, create ReportData."""
    start = time.perf_counter()

    warnings: List[str] = []
    errors: List[str] = []

    catalogue = load_catalogue(products_path, warnings)
    sales = load_sales(sales_path)
    line_items, total_sum = compute_totals(catalogue, sales, warnings, errors)
    elapsed = time.perf_counter() - start

    return ReportData(
        line_items=line_items,
        total_sum=total_sum,
        elapsed=elapsed,
        warnings=warnings,
        errors=errors,
        include_messages=include_messages,
    )


def write_report(report: ReportData, outdir: Path) -> None:
    """Print report and write SalesResults.txt to outdir."""
    output = format_report(report)
    print(output)

    try:
        outdir.mkdir(parents=True, exist_ok=True)
        out_path = outdir / "SalesResults.txt"
        out_path.write_text(output, encoding="utf-8")
        print(f"\nResults written to {out_path}")
    except OSError as exc:
        print(f"ERROR: Could not write SalesResults.txt: {exc}")
        sys.exit(1)


def main() -> None:
    """Entry point: parse args, run, and write report."""
    products_path, sales_path, include_messages, outdir = parse_args(sys.argv)
    report = run(products_path, sales_path, include_messages)
    write_report(report, outdir)


if __name__ == "__main__":
    main()
