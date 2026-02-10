# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""validateResults.py

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
from typing import Dict, List, Optional, Sequence

TOTAL_PATTERN = re.compile(
    r"^\s*GRAND\s+TOTAL:\s*\$?([0-9_,]+(?:\.[0-9]{1,2})?)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CaseResult:
    """Container holding the validation outcome for a single test case.

    Attributes
    ----------
    case : str
        The case name (e.g., "TC1").
    expected : float
        The expected total read from the expected results file.
    got : Optional[float]
        The computed total parsed from the case's SalesResults.txt, or None if
        it could not be found/parsed.
    diff : Optional[float]
        The difference `got - expected`, or None when `got` is None.
    passed : bool
        Whether the absolute difference is within the allowed tolerance.
    path : Path
        The path to the SalesResults.txt inspected for this case.
    """
    case: str
    expected: float
    got: Optional[float]
    diff: Optional[float]
    passed: bool
    path: Path


def parse_expected(path: Path) -> Dict[str, float]:
    """Parse expected totals from a simple TSV/whitespace file.

    Ignores the header line 'TOTAL' if present. Each subsequent non-empty line
    must be: <CASE><TAB><number> (tabs) or <CASE> <number> (whitespace).

    Parameters
    ----------
    path : Path
        Path to the expected results text file.

    Returns
    -------
    Dict[str, float]
        Mapping of case name to expected numeric total.
    """
    mapping: Dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.upper() == "TOTAL":
            continue
        parts = re.split(
            r"\s+", line) if "\t" not in line else line.split("\t")
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
    """Extract the grand total from a SalesResults.txt file.

    Parameters
    ----------
    report_path : Path
        Path to the case's SalesResults.txt.

    Returns
    -------
    Optional[float]
        The parsed grand total, or None if not found/parsable.
    """
    text = report_path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        match = TOTAL_PATTERN.match(line)
        if match:
            raw = match.group(1).replace(",", "").replace("_", "")
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
    """Validate the computed totals for a list of cases.

    Parameters
    ----------
    expected_map : Dict[str, float]
        Mapping of case name to expected total.
    cases : Sequence[str]
        Sequence of case names (e.g., ["TC1", "TC2", "TC3"]).
    base_dir : Path
        Base directory containing <CASE>/SalesResults.txt.
    tolerance : float
        Allowed absolute difference between expected and actual.

    Returns
    -------
    List[CaseResult]
        A list of results, one per case.
    """
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


def create_line(r: CaseResult) -> str:
    """Format a single table row for console output.

    Parameters
    ----------
    r : CaseResult
        The case result to render.

    Returns
    -------
    str
        A formatted, fixed-width line containing Expected / Got / Diff / Pass.
    """
    exp = "N/A" if r.expected != r.expected else f"${r.expected:,.2f}"
    got = "N/A" if r.got is None else f"${r.got:,.2f}"
    diff = "N/A" if r.diff is None else f"{r.diff:+,.2f}"
    passes = "✅ Yes" if r.passed else "❌  No"
    return f"{r.case:6} {exp:>14} {got:>14} {diff:>12} {passes:>6}"


def format_console(results: List[CaseResult], tolerance: float) -> str:
    """Create the multi-line console report for all cases.

    Parameters
    ----------
    results : List[CaseResult]
        Case results to render.
    tolerance : float
        Tolerance used for pass/fail decisions (displayed in header).

    Returns
    -------
    str
        The report text to print to stdout.
    """
    lines: List[str] = []
    lines.append("EXPECTED VS ACTUAL RESULTS")
    lines.append("=" * 72)
    lines.append(f"Tolerance: ±{tolerance:.4f}")
    lines.append("")
    lines.append(
        f"{'CASE':6} {'EXPECTED':>14} {'GOT':>14} {'DIFF':>12} {'PASS':>6}")
    lines.append("-" * 72)
    for res in results:
        lines.append(create_line(res))
    lines.append("-" * 72)
    passed_count = sum(1 for res in results if res.passed)
    lines.append(f"Passed: {passed_count}/{len(results)}")
    lines.append("=" * 72)
    return "\n".join(lines)


def write_csv(results: List[CaseResult], csv_path: Path) -> None:
    """Write machine-readable results to a CSV file.

    Columns: case, expected, got, diff, passed, report_path

    Parameters
    ----------
    results : List[CaseResult]
        The results to write.
    csv_path : Path
        Destination CSV path (parent folders will be created by caller).
    """
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["case", "expected", "got",
                        "diff", "passed", "report_path"])
        for res in results:
            writer.writerow(
                [
                    res.case,
                    res.expected,
                    "" if res.got is None else res.got,
                    "" if res.diff is None else res.diff,
                    res.passed,
                    str(res.path),
                ]
            )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments for the results validator.

    Parameters
    ----------
    argv : Optional[Sequence[str]]
        Raw argv; if None, argparse uses sys.argv.

    Returns
    -------
    argparse.Namespace
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Validate SalesResults.txt totals against an expected results file"
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
    """
    Entry point: parse args, validate cases, print and (optionally) write CSV.

    Parameters
    ----------
    argv : Optional[Sequence[str]]
        Raw argv; if None, argparse uses sys.argv.

    Returns
    -------
    int
        Process exit code: 0 on success, non-zero on I/O/CSV failures.
    """
    args = parse_args(argv)
    expected_map = parse_expected(args.expected)
    results = validate_cases(expected_map, args.cases,
                             args.base_dir, args.tolerance)
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
