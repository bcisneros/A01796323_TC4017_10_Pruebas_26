#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
computeStatistics.py

Command-line program that reads a file containing numeric items and computes
descriptive statistics using only basic algorithms (no math/statistics libs):
- mean
- median
- mode
- variance (population and sample)
- standard deviation (population and sample)

It prints results to console and writes them to 'StatisticsResults.txt',
with aligned columns for readability.

Invalid tokens are reported to the console (stderr), and execution continues.

Usage:
    python computeStatistics.py fileWithData.txt
"""

import sys
import time


def parse_numbers_from_file(path):
    """
    Parse numbers from a text file.
    Accepts whitespace or comma separated tokens.
    Invalid tokens are reported to the console, and ignored.

    Returns:
        list[float]: list of parsed numbers (floats).
    """
    numbers = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line_no, raw in enumerate(fh, start=1):
                # Support commas and whitespace as separators
                line = raw # .replace(",", " ")
                process_line(numbers, line_no, line)
    except FileNotFoundError:
        print(f"[FATAL] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"[FATAL] Cannot read file '{path}': {exc}", file=sys.stderr)
        sys.exit(1)

    return numbers


def process_line(numbers, line_no, line):
    """Process a single line, updating numbers list with valid floats."""
    for token in line.split():
        try:
            # Accept ints or floats (including scientific notation)
            value = float(token)
            numbers.append(value)
        except ValueError:
            print(
                f"[ERROR] Invalid token at line {line_no}: '{token}'",
                file=sys.stderr,
            )
            numbers.append(0.0)  # Treat invalid tokens as zero for statistics


def merge(left, right):
    """Merge step for merge sort."""
    merged = []
    i = 0
    j = 0
    len_left = len(left)
    len_right = len(right)

    while i < len_left and j < len_right:
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append remaining
    while i < len_left:
        merged.append(left[i])
        i += 1
    while j < len_right:
        merged.append(right[j])
        j += 1

    return merged


def merge_sort(arr):
    """
    Stable O(n log n) merge sort implemented from scratch.
    Returns a new sorted list (does not modify the input list).
    """
    n = len(arr)
    if n <= 1:
        return arr[:]
    mid = n // 2
    left_sorted = merge_sort(arr[:mid])
    right_sorted = merge_sort(arr[mid:])
    return merge(left_sorted, right_sorted)


def compute_mean(data):
    """Compute arithmetic mean using a basic loop."""
    n = len(data)
    if n == 0:
        return None
    total = 0.0
    for x in data:
        total += x
    return total / n


def compute_median(sorted_data):
    """
    Compute median assuming the data is already sorted.
    Uses a basic index-based approach.
    """
    n = len(sorted_data)
    if n == 0:
        return None
    mid = n // 2
    if n % 2 == 1:
        return sorted_data[mid]
    # Even count: average of the two middle values
    return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0


def compute_mode(data):
    """
    Compute mode(s) using a frequency dictionary via basic loops.
    Returns:
        - list of modes if one or more values share the highest frequency (>1)
        - empty list if all values occur exactly once (i.e., no mode)
    """
    n = len(data)
    if n == 0:
        return []

    freq = {}
    for x in data:
        # Dictionary counting via basic logic
        if x in freq:
            freq[x] += 1
        else:
            freq[x] = 1

    # Find max frequency
    max_freq = 0
    for _, count in freq.items():
        max_freq = max(max_freq, count)

    if max_freq <= 1:
        # No repeated values -> no mode
        return []

    # Collect all values with max frequency
    modes = []
    for value, count in freq.items():
        if count == max_freq:
            modes.append(value)

    # Sort modes for stable presentation (using our merge sort)
    modes_sorted = merge_sort(modes)
    return modes_sorted


def compute_variance_population(data, mean_value):
    """
    Population variance: average of squared deviations from the mean.
    """
    n = len(data)
    if n == 0:
        return None
    total_sq_dev = 0.0
    for x in data:
        diff = x - mean_value
        total_sq_dev += diff * diff
    return total_sq_dev / n


def compute_variance_sample(data, mean_value):
    """
    Sample variance: sum of squared deviations divided by (n - 1).
    Requires n >= 2.
    """
    n = len(data)
    if n < 2:
        return None
    total_sq_dev = 0.0
    for x in data:
        diff = x - mean_value
        total_sq_dev += diff * diff
    return total_sq_dev / (n - 1)


def sqrt_newton(value, tol=1e-12, max_iter=100):
    """
    Compute square root using Newton's method (no math.sqrt).
    Assumes value >= 0.
    """
    if value is None:
        return None
    if value < 0:
        return None
    if value == 0:
        return 0.0

    # Initial guess
    x = value
    for _ in range(max_iter):
        prev = x
        x = 0.5 * (x + value / x)
        if x == 0:
            break
        if prev == 0:
            continue
        # Convergence check
        if abs(x - prev) <= tol * max(1.0, abs(prev)):
            break
    return x


def format_number(x, decimals=6):
    """Format numbers without forcing trailing zeros.
    Integers show no decimals; floats show only necessary precision."""
    if x is None:
        return "N/A"

    # if integer, show as int
    if float(x).is_integer():
        return str(int(x))

    # if float, format with given decimals but strip trailing zeros
    s = f"{x:.{decimals}f}"  # format with fixed decimals
    s = s.rstrip("0")  # remove zeros at the end
    if s.endswith("."):
        s = s[:-1]  # remove trailing dot if no decimals left

    return s


def write_results(path, content):
    """Write content to a file."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        print(f"[ERROR] Could not write results file: {exc}", file=sys.stderr)


def build_aligned_stats_table(rows, input_path):
    """
    Build an aligned text table for statistics.

    Args:
        rows (list[tuple[str, str]]): Each tuple is (metric_label, value_str)

    Returns:
        str: full table text.
    """
    header_left = "Metric"
    header_right = "Value"

    left_width = len(header_left)
    right_width = len(header_right)

    # Compute max widths using max(...) to satisfy pylint R1731
    for label, value in rows:
        left_width = max(left_width, len(label))
        right_width = max(right_width, len(value))

    sep = "  |  "
    left_header_side = header_left.ljust(left_width)
    right_header_side = header_right.rjust(right_width)
    header = left_header_side + sep + right_header_side
    line_sep = sep.replace("|", "+").replace(" ", "-")
    rule = "-" * left_width + line_sep + "-" * right_width

    lines = []
    lines.append(f"=== Descriptive Statistics ({input_path}) ===")
    lines.append("")
    lines.append(header)
    lines.append(rule)

    for label, value in rows:
        line = label.ljust(left_width) + sep + value.rjust(right_width)
        lines.append(line)

    lines.append("")
    return "\n".join(lines)


def compute_all_statistics(data):
    """
    Compute all requested statistics using basic algorithms.

    Returns:
        dict: {
            'count', 'mean', 'median', 'modes',
            'var_pop', 'std_pop', 'var_sam', 'std_sam'
        }
    """
    result = {
        "count": len(data),
        "mean": None,
        "median": None,
        "modes": [],
        "var_pop": None,
        "std_pop": None,
        "var_sam": None,
        "std_sam": None,
    }

    if result["count"] == 0:
        return result

    sorted_data = merge_sort(data)
    mean_value = compute_mean(data)
    median_value = compute_median(sorted_data)
    modes = compute_mode(data)

    var_pop = compute_variance_population(data, mean_value)
    std_pop = sqrt_newton(var_pop) if var_pop is not None else None

    var_sam = compute_variance_sample(data, mean_value)
    std_sam = sqrt_newton(var_sam) if var_sam is not None else None

    result["mean"] = mean_value
    result["median"] = median_value
    result["modes"] = modes
    result["var_pop"] = var_pop
    result["std_pop"] = std_pop
    result["var_sam"] = var_sam
    result["std_sam"] = std_sam
    return result


def prepare_rows(stats, elapsed_seconds):
    """
    Prepare the (metric, value) rows for aligned output.
    """
    count = stats["count"]
    rows = [
        ("Count", str(count)),
        ("Mean", format_number(stats["mean"], 7)),
        ("Median", format_number(stats["median"], 7)),
        ("Mode", prepare_mode_string(count, stats["modes"])),
        ("Population Std Dev", format_number(stats["std_pop"], 7)),
        ("Population Variance", format_number(stats["var_pop"], 6)),
        ("Sample Std Dev", format_number(stats["std_sam"], 6)),
        ("Sample Variance", format_number(stats["var_sam"], 5)),
        ("Elapsed Time (seconds)", format_number(elapsed_seconds, 7)),
    ]
    return rows


def prepare_mode_string(count, modes):
    """
    Prepare the mode string for output.
    """
    if len(modes) == 0 and count > 0:
        return "#N/A"
    if len(modes) == 1:
        return format_number(modes[0], 6)
    if len(modes) > 1:
        parts = [format_number(v, 6) for v in modes]
        return "[" + ", ".join(parts) + "]"
    return "#N/A"

def main():
    """
    Entry point: accept one or multiple input files, compute statistics per file,
    print all results, and write one combined report at the end.
    """
    if len(sys.argv) < 2:
        print(
            "Usage:\n  python computeStatistics.py file1.txt [file2.txt ... fileN.txt]",
            file=sys.stderr,
        )
        sys.exit(2)

    input_paths = sys.argv[1:]
    all_sections = []
    overall_start = time.perf_counter()

    for input_path in input_paths:
        # Per-file timing
        start_time = time.perf_counter()
        try:
            data = parse_numbers_from_file(input_path)
        except OSError as exc:
            print(f"[FATAL] Cannot read file '{input_path}': {exc}", file=sys.stderr)
            # Keep going with next files
            continue

        stats = compute_all_statistics(data)
        elapsed = time.perf_counter() - start_time

        # Build a formatted section for this file
        section_text = build_aligned_stats_table(
            prepare_rows(stats, elapsed),
            input_path
        )
        all_sections.append(section_text)

    # If none succeeded, stop gracefully
    if not all_sections:
        print("[ERROR] No valid inputs were processed.", file=sys.stderr)
        sys.exit(1)

    # Optional: overall elapsed for the batch (not part of each table)
    overall_elapsed = time.perf_counter() - overall_start
    footer = (
        "\n=== Batch Summary ===\n"
        f"Files processed: {len(all_sections)}\n"
        f"Total elapsed time (seconds): {overall_elapsed:.6f}\n"
    )

    # Join all sections with a clear separator
    combined_report = "\n".join(all_sections) + footer

    # Output to console and single results file (overwrite)
    print(combined_report)
    write_results("results/StatisticsResults.txt", combined_report)

if __name__ == "__main__":
    main()
