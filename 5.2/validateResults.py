# -*- coding: utf-8 -*-
"""validate_results.py

Validate computed sales results against expected totals for each test case.

Usage:
    python validate_results.py --expected expected.txt --cases TC1 TC2 TC3 \
        [--base-dir .] [--tolerance 0.01]

Assumptions
-----------
- Your program writes per-case reports at: <base-dir>/<CASE>/SalesResults.txt
  e.g., TC1/SalesResults.txt
- Each report contains a line like: "GRAND TOTAL: $2,481.86"
- The expected file contains lines in the format:
      TOTAL
      TC1\t2481.86
      TC2\t166568.23
      TC3\t165235.37

Output
------
Prints a table with: Case, Expected, Got, Diff, Pass/Fail
Also writes a machine-readable CSV next to the expected file.
"""
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

TOTAL_PATTERN = re.compile(
    r"^\s*GRAND\s+TOTAL:\s*\$?([0-9_,]+(?:\.[0-9]{1,2})?)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CaseResult:
    case: str
    expected: float
    got: Optional[float]
    diff: Optional[float]
    passed: bool
    path: Path


def parse_expected(path: Path) -> Dict[str, float]:
    """Parse expected totals from a simple TSV-like file.

    Ignores the header line 'TOTAL' if present.
    Each subsequent non-empty line must be: <CASE> <tab> <number>
    """
    mapping: Dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.upper() == "TOTAL":
            continue
        parts = re.split(r"\s+", line) if "\t" not in line else line.split("\t")
        if len(parts) < 2:
            continue
        case, num = parts[0], parts[1]
        try:
            mapping[case] = float(num)
        except ValueError:
            # skip malformed numeric
            continue
    return mapping


def extract_total(report_path: Path) -> Optional[float]:
    """Extract the grand total from a SalesResults.txt file."""
    text = report_path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        m = TOTAL_PATTERN.match(line)
        if m:
            raw = m.group(1).replace(",", "").replace("_", "")
            try:
                return float(raw)
            except ValueError:
                return None
    return None


def validate_cases(
    expected_map: Dict[str, float],
    cases: Sequence[str],
    base_dir: Path,
    tolerance: float,
) -> List[CaseResult]:
    results: List[CaseResult] = []
    for case in cases:
        report_path = base_dir / case / "SalesResults.txt"
        got = extract_total(report_path) if report_path.exists() else None
        exp = expected_map.get(case)
        if exp is None:
            # If case not in expected file, mark as failed
            results.append(
                CaseResult(
                    case=case,
                    expected=float("nan"),
                    got=got,
                    diff=None,
                    passed=False,
                    path=report_path,
                )
            )
            continue
        if got is None:
            results.append(
                CaseResult(
                    case=case,
                    expected=exp,
                    got=None,
                    diff=None,
                    passed=False,
                    path=report_path,
                )
            )
            continue
        diff = got - exp
        passed = abs(diff) <= tolerance
        results.append(
            CaseResult(
                case=case,
                expected=exp,
                got=got,
                diff=diff,
                passed=passed,
                path=report_path,
            )
        )
    return results


def format_console(results: List[CaseResult], tolerance: float) -> str:
    lines: List[str] = []
    lines.append("EXPECTED VS ACTUAL RESULTS")
    lines.append("=" * 72)
    lines.append(f"Tolerance: ±{tolerance:.4f}")
    lines.append("")
    lines.append(f"{'CASE':6} {'EXPECTED':>14} {'GOT':>14} {'DIFF':>12} {'PASS':>6}")
    lines.append("-" * 72)
    for r in results:
        exp_str = "N/A" if r.expected != r.expected else f"${r.expected:,.2f}"  # NaN check
        got_str = "N/A" if r.got is None else f"${r.got:,.2f}"
        diff_str = "N/A" if r.diff is None else f"{r.diff:+,.2f}"
        pass_str = "✅ Yes" if r.passed else "❌  No"
        lines.append(
            f"{r.case:6} {exp_str:>14} {got_str:>14} {diff_str:>12} {pass_str:>6}"
        )
    lines.append("-" * 72)
    passed_count = sum(1 for r in results if r.passed)
    lines.append(f"Passed: {passed_count}/{len(results)}")
    lines.append("=" * 72)
    return "\n".join(lines)


def write_csv(results: List[CaseResult], csv_path: Path) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["case", "expected", "got", "diff", "passed", "report_path"])
        for r in results:
            writer.writerow(
                [
                    r.case,
                    r.expected,
                    "" if r.got is None else r.got,
                    "" if r.diff is None else r.diff,
                    r.passed,
                    str(r.path),
                ]
            )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate SalesResults.txt totals against an expected results file."
        )
    )
    parser.add_argument(
        "--expected",
        required=True,
        type=Path,
        help="Path to expected results file (TSV-like).",
    )
    parser.add_argument(
        "--cases",
        nargs="+",
        required=True,
        help="List of test case folder names (e.g., TC1 TC2 TC3).",
    )
    parser.add_argument(
        "--base-dir",
        default=Path("."),
        type=Path,
        help="Base directory containing <CASE>/SalesResults.txt (default: .)",
    )
    parser.add_argument(
        "--tolerance",
        default=0.001,
        type=float,
        help="Numeric tolerance for comparison (default: 0.001)",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        help="Optional CSV output path for machine-readable results.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    expected_map = parse_expected(args.expected)
    results = validate_cases(expected_map, args.cases, args.base_dir, args.tolerance)
    report = format_console(results, args.tolerance)
    print(report)

    if args.csv_path:
        try:
            args.csv_path.parent.mkdir(parents=True, exist_ok=True)
            write_csv(results, args.csv_path)
            print(f"CSV written to {args.csv_path}")
        except OSError as exc:
            print(f"ERROR: Could not write CSV: {exc}")
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
