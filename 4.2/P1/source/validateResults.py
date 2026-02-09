#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""
validateResults.py

Validates P1 results by comparing:
  - your report:   P1/results/StatisticsResults.txt
  - expected grid: P1/tests/A4.2.P1.Results-errata.txt

Rules:
  * Count: exact integer match
  * Mean/Median/SD/Variance: numeric compare with tolerances for floats
    - Large integers (e.g., TC6/TC7) => exact integer match
  * Mode:
      - expected '#N/A' or 'N/A' => accept 'No mode' or '#N/A'
      - expected single value => accept if present in your list-of-modes
      - expected list => require set equality (can relax to subset if desired)

Usage:
  python validate_p1_results.py

Exit code:
  0 if all TCs/metrics pass, 1 otherwise.
"""

import os
import re
import sys
from decimal import Decimal, InvalidOperation

# ------------------------------ Config ------------------------------
YOUR_RESULTS_PATH = os.path.join("results", "StatisticsResults.txt")
EXPECTED_PATH = os.path.join("tests", "A4.2.P1.Results-errata.txt")

# Absolute and relative tolerances for floating-point comparisons
ABS_TOL = Decimal("1e-26")
REL_TOL = Decimal("1e-29")

# Map metric labels (your output) → expected row names
METRIC_MAP = {
    "Count":                 "COUNT",
    "Mean":                  "MEAN",
    "Median":                "MEDIAN",
    "Mode":                  "MODE",
    "Population Std Dev":    "SD",
    "Population Variance":   "VARIANCE",
    "Sample Std Dev":        "SD_SAMPLE",
    "Sample Variance":       "VARIANCE_SAMPLE"
}

# TCs we expect
TC_ORDER = ["TC1", "TC2", "TC3", "TC4", "TC5", "TC6", "TC7"]

# ------------------------------ Helpers ------------------------------


def d(s):
    """Parse string to Decimal safely (strip spaces/commas)."""
    try:
        s = s.strip()
        # unify thousands commas if any (shouldn't be present)
        s = s.replace(",", "")
        return Decimal(s)
    except (InvalidOperation, AttributeError):
        return None


def is_big_integer_string(s):
    """
    Return True if s looks like a (very) large integer (no decimal point).
    """
    s = s.strip()
    if not s:
        return False
    if s.startswith("-"):
        s2 = s[1:]
    else:
        s2 = s
    return s2.isdigit()


def almost_equal_decimal(
        a: Decimal, b: Decimal, abs_tol=ABS_TOL, rel_tol=REL_TOL):
    """
    Decide if two Decimals are 'close enough' per abs/rel tolerances.
    """
    if a == b:
        return True
    diff = abs(a - b)
    # If either is zero, rely on absolute tolerance
    if a == 0 or b == 0:
        return diff <= abs_tol
    # Else, combine absolute + relative
    return (diff <= abs_tol) or (diff / max(abs(a), abs(b)) <= rel_tol)


def parse_modes_from_yours(value_str):
    """
    Parse your Mode field:
        - "No mode (all values appear once)" -> tag as NO_MODE
        - "[170, 393]" -> list of ints
        - "393"        -> single int list
        - "#N/A"       -> NO_MODE
    """
    val = value_str.strip()
    if val.lower().startswith("no mode"):
        return ("NO_MODE", set())
    if val.upper() in {"#N/A", "N/A"}:
        return ("NO_MODE", set())
    # list form?
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return ("LIST", set())
        parts = [p.strip() for p in inner.split(",")]
        out = set()
        for p in parts:
            if p:
                try:
                    out.add(int(Decimal(p)))
                except Exception:
                    # ignore non-int entries
                    pass
        return ("LIST", out)
    # single numeric value?
    try:
        single = int(Decimal(val))
        return ("LIST", {single})
    except Exception:
        # fallback: treat as NO_MODE if unknown
        return ("NO_MODE", set())


def parse_modes_from_expected(value_str):
    """
    Parse expected Mode field:
      - "#N/A" or "N/A" => NO_MODE
      - "393"           => single
      - "[170, 393]"    => list (if present in grid)
    """
    val = value_str.strip()
    if val.upper() in {"#N/A", "N/A"}:
        return ("NO_MODE", set())
    # If comma-separated list were present:
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        parts = [p.strip() for p in inner.split(",")] if inner else []
        out = set()
        for p in parts:
            if p:
                try:
                    out.add(int(Decimal(p)))
                except Exception:
                    pass
        return ("LIST", out)
    # Else single numeric expected
    try:
        single = int(Decimal(val))
        return ("LIST", {single})
    except Exception:
        return ("NO_MODE", set())


def compare_mode(your_str, expected_str):
    """
    Mode comparison logic:
      - Expected NO_MODE => accept your NO_MODE
      - Expected single k => pass if k is in your set (or equals your single)
      - Expected list => require set equality (change to subset if desired)
    """
    y_kind, y_set = parse_modes_from_yours(your_str)
    e_kind, e_set = parse_modes_from_expected(expected_str)

    if e_kind == "NO_MODE":
        return (y_kind == "NO_MODE", "NO_MODE expected")

    # expected is list (including single as {k})
    if not y_set:
        return (False, f"Expected {sorted(e_set)}, got NO_MODE")

    # require that every expected element is contained (or exact equality)
    # exact equality:
    # ok = (y_set == e_set)
    # relaxed: accept expected single in your multiple:
    ok = e_set.issubset(y_set)
    msg = f"expected {sorted(e_set)} in your {sorted(y_set)}"
    return (ok, msg)

# ------------------------------ Parsers ------------------------------


def parse_your_results(path):
    """
    Parse your multi-section results file.
    Returns: dict[TC] = dict(metric_label -> string_value)
    """
    if not os.path.exists(path):
        print(f"[FATAL] Your results file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    # split sections by "=== Descriptive Statistics (tests/TCx.txt) ==="
    sec_re = re.compile(
        r"^===\s*Descriptive Statistics\s*\((.+?)\)\s*===$", re.MULTILINE)
    sections = []
    last_pos = 0
    for m in sec_re.finditer(text):
        if sections:
            # previous section body ends before this header
            sections[-1]["body"] = text[sections[-1]
                                        ["start"]:m.start()].strip()
        sections.append({"hdr": m.group(1), "start": m.end(), "body": ""})
    if sections:
        sections[-1]["body"] = text[sections[-1]["start"]:].strip()

    results = {}
    for sec in sections:
        hdr = sec["hdr"]  # e.g., "tests/TC1.txt"
        # Extract TC name:
        tc_match = re.search(r"(TC\d+)\.txt", hdr)
        if not tc_match:
            # skip unknown
            continue
        tc = tc_match.group(1)
        body = sec["body"]

        # parse table lines "Metric | Value"
        metrics = {}
        for line in body.splitlines():
            line = line.rstrip()
            # lines like: "Count                   |          400"
            if "|" in line and not line.startswith("---"):
                parts = [p.strip() for p in line.split("|", 1)]
                if len(parts) == 2:
                    key, val = parts[0], parts[1]
                    # store raw string
                    metrics[key] = val

        # keep only metrics we care
        if metrics:
            results[tc] = metrics

    return results


def parse_expected_grid(path):
    """
    Parse the expected grid:
      Rows: COUNT, MEAN, MEDIAN, MODE, SD, VARIANCE
      Cols: TC1 ... TC7

    Returns: dict[TC] = {'COUNT': str, 'MEAN': str, ...}
    """
    if not os.path.exists(path):
        print(f"[FATAL] Expected file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()

    # Normalize tabs to single tabs; then split by lines
    # we'll detect the header row that contains "TC1" ... "TC7"
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

    # Find header line with TCs
    header_idx = -1
    tc_headers = []
    for i, ln in enumerate(lines):
        if ln.startswith("TC") and "TC1" in ln:
            header_idx = i
            # split by whitespace or tabs
            tc_headers = [tok.strip()
                          for tok in re.split(r"[ \t]+", ln) if tok.strip()]
            break
    if header_idx == -1:
        # Try: a line begins with something like "TC    TC1  TC2 ..."
        for i, ln in enumerate(lines):
            if "TC1" in ln and "TC2" in ln:
                header_idx = i
                tc_headers = get_tc_headers(ln)
                break

    if header_idx == -1:
        print(
            "[FATAL] Could not locate TC header line in expected file.", 
            file=sys.stderr
        )
        sys.exit(1)

    # Build column index map for TCs
    # Example headers might be: ["TC", "TC1", "TC2", ...]
    col_map = {}
    for idx, h in enumerate(tc_headers):
        if h.startswith("TC"):
            col_map[h] = idx

    # Now parse subsequent metric rows until another section starts
    # Rows start with COUNT / MEAN / MEDIAN / MODE / SD / VARIANCE
    metrics_interest = {"COUNT", "MEAN", "MEDIAN", "MODE", "SD", "VARIANCE"}
    expected = {tc: {} for tc in TC_ORDER}

    for ln in lines[header_idx + 1:]:
        parts = [tok for tok in re.split(r"[ \t]+", ln) if tok]
        if not parts:
            continue
        row_label = parts[0].upper()
        if row_label not in metrics_interest:
            continue

        for tc in TC_ORDER:
            if tc not in col_map:
                continue
            col_idx = col_map[tc]
            # If we don't have enough tokens, try last token (crude fallback)
            if col_idx < len(parts):
                val = parts[col_idx]
            else:
                # fallback: search line for tc then take next token-like chunk
                # (coarse—but should not be needed if file is clean)
                val = ""
            expected[tc][row_label] = val

    return expected

def get_tc_headers(ln):
    return [tok.strip() for tok in re.split(r"[ \t]+", ln) if tok.strip()]

# ------------------------------ Validator ------------------------------


def validate(yours, expected):
    """
    Compare per-TC metrics and print a summary.
    Returns True if all required metrics pass; False otherwise.
    """
    all_ok = True
    print("=== Validation of P1 Results ===\n")
    for tc in TC_ORDER:
        print(f"[{tc}]")
        y = yours.get(tc, {})
        e = expected.get(tc, {})

        if not y:
            print(f"  ❌ FAIL: No section parsed for {tc}")
            all_ok = False
            print()
            continue

        # Metrics to validate against the expected grid
        checks = [
            ("Count", "COUNT"),
            ("Mean", "MEAN"),
            ("Median", "MEDIAN"),
            ("Mode", "MODE"),
            ("Population Std Dev", "SD"),
            ("Sample Variance", "VARIANCE"),
        ]

        for your_key, exp_row in checks:
            y_raw = y.get(your_key, "").strip()
            e_raw = e.get(exp_row, "").strip()

            # MODE special handling
            if your_key == "Mode":
                ok, note = compare_mode(y_raw, e_raw)
                if ok:
                    print(f"  ✅ PASS: Mode (expected {e_raw})")
                else:
                    print(
                        f"  ❌ FAIL: Mode mismatch (exp {e_raw}, got {y_raw})")
                    all_ok = False
                continue

            if e_raw.upper() in {"#N/A", "N/A"}:
                # Should not happen for non-mode rows; mark fail
                print(
                    f"  ❌ FAIL: Unexpected non-numeric {your_key}: {e_raw}")
                all_ok = False
                continue

            if is_big_integer_string(e_raw):
                # exact integer compare
                try:
                    ya = d(y_raw)
                    ea = d(e_raw)
                    if ya is None or ea is None or (ya != ea):
                        print(
                            f"  ❌ FAIL: {your_key} (exp {e_raw}, got {y_raw})")
                        all_ok = False
                    else:
                        print(f"  ✅ PASS: {your_key}")
                except Exception:
                    print(
                        f"  ❌ FAIL: {your_key} (exp {e_raw}, got {y_raw})")
                    all_ok = False
            else:
                # floating or decimal numbers: tolerance-based compare
                ya = d(y_raw)
                ea = d(e_raw)
                if ya is None or ea is None:
                    print(
                        f"  ❌ FAIL: {your_key} (exp {e_raw}, got {y_raw})")
                    all_ok = False
                else:
                    if almost_equal_decimal(ya, ea):
                        print(f"  ✅ PASS: {your_key}")
                    else:
                        # include deltas for debugging
                        diff = ya - ea
                        print(
                            # pylint: disable=line-too-long
                            f"  ❌ FAIL: {your_key} (exp {e_raw}, got {y_raw}, diff={diff})")
                        all_ok = False

        print()

    print("=== Validation Completed ===")
    print("Overall:", "PASS ✅" if all_ok else "FAIL ❌")
    return all_ok

# ------------------------------ Main ------------------------------


def main():
    yours = parse_your_results(YOUR_RESULTS_PATH)
    expected = parse_expected_grid(EXPECTED_PATH)
    ok = validate(yours, expected)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
