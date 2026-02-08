#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
convertNumbers.py

Command-line program that reads a file containing numeric items (integers with
optional sign) and converts each valid number to binary and hexadecimal using
basic algorithms (no bin/hex/format or external libraries).

It prints results to console and writes them to 'ConvertionResults.txt',
with aligned columns for readability. Each converted number includes the
source line number where it appeared in the input file.

Invalid tokens are reported to the console (stderr), and execution continues.

Usage:
    python convertNumbers.py fileWithData.txt
"""

import sys
import time

def pow_int(base, exp):
    """Compute base**exp using integer multiplications (no math.pow)."""
    result = 1
    for _ in range(exp):
        result *= base
    return result


def to_base_string_positive(n, base):
    """
    Convert a NON-NEGATIVE integer n to base (2 or 16) without leading zeros.
    Uses the same repeated-division approach as to_base_string, but assumes n >= 0.
    """
    if n == 0:
        return "0"
    digits_map = "0123456789ABCDEF"
    chars = []
    while n > 0:
        n, rem = divmod(n, base)
        chars.append(digits_map[rem])
    chars.reverse()
    return "".join(chars)


def twos_complement_bin(value, bits=10):
    """
    Return a fixed-width two's-complement binary string for 'value' using 'bits' bits.
    Example: value=-39, bits=10 -> '1111011001'
    """
    if bits <= 0:
        return "0"
    modulus = pow_int(2, bits)          # 2^bits
    if value >= 0:
        # For non-negative numbers, follow the expected (no padding with leading zeros)
        return to_base_string_positive(value, 2)
    # Two's-complement representation in 'bits'
    m = value % modulus                  # Python % yields a non-negative remainder
    s = to_base_string_positive(m, 2)
    # Ensure EXACTLY 'bits' bits for negatives
    if len(s) < bits:
        s = ("0" * (bits - len(s))) + s
    return s


def twos_complement_hex(value, hex_width=10):
    """
    Return a fixed-width two's-complement HEX string (uppercase) for 'value'
    using 'hex_width' hexadecimal digits (i.e., 4*hex_width bits).
    Example: value=-39, hex_width=10 -> 'FFFFFFFFD9'
    """
    if hex_width <= 0:
        return "0"
    modulus = pow_int(16, hex_width)     # 16^hex_width == 2^(4*hex_width)
    if value >= 0:
        # For non-negative numbers, follow the expected (no padding with leading zeros)
        return to_base_string_positive(value, 16)
    # Two's-complement representation in 'hex_width' hex digits
    m = value % modulus                  # non-negative remainder in range [0, 16^hex_width)
    s = to_base_string_positive(m, 16)
    # Left-pad with zeros to reach exact width (for negatives, digits will naturally start with 'F' when needed)
    if len(s) < hex_width:
        s = ("0" * (hex_width - len(s))) + s
    return s


def parse_int_token(token):
    """
    Parse a token as a base-10 signed integer using basic character processing.
    Accepts an optional leading '+' or '-'.
    Returns:
        int on success, or None if the token is not a valid integer.
    """
    if token is None:
        return None
    token = token.strip()
    if token == "":
        return None

    sign = 1
    start = 0

    first = token[0]
    if first == "+":
        start = 1
    elif first == "-":
        sign = -1
        start = 1

    if start == len(token):
        # Token is only '+' or '-' -> invalid
        return None

    value = 0
    for i in range(start, len(token)):
        c = token[i]
        if "0" <= c <= "9":
            digit = ord(c) - ord("0")
            value = value * 10 + digit
        else:
            # Any non-digit (e.g., '.', 'e', letters) invalidates the token
            return None

    return sign * value


def to_base_string(value, base):
    """
    Convert a signed integer 'value' to a string in the given 'base'
    (supports base 2 or 16) using repeated division and remainders.
    Does not use bin(), hex(), or format().
    """
    if base not in (2, 16):
        raise ValueError("Supported bases are 2 and 16.")

    if value == 0:
        return "0"

    digits_map = "0123456789ABCDEF"

    sign = ""
    n = value
    if n < 0:
        sign = "-"
        n = -n  # make positive

    chars = []
    # Repeated division method
    while n > 0:
        remainder = n % base
        chars.append(digits_map[remainder])
        n = n // base

    # Reverse to get the correct order
    chars = chars[::-1]
    return sign + "".join(chars)


def parse_integers_from_file(path):
    """
    Parse signed integers from a text file. Accepts whitespace- or
    comma-separated tokens. Invalid tokens are reported to stderr and ignored.

    Returns:
        list[tuple[int, int]]: list of (line_no, parsed_integer) pairs.
    """
    items = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line_no, raw in enumerate(fh, start=1):
                line = raw.replace(",", " ")
                tokens = line.split()
                process_tokens(items, line_no, tokens)
    except FileNotFoundError:
        print(f"[FATAL] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"[FATAL] Cannot read file '{path}': {exc}", file=sys.stderr)
        sys.exit(1)

    return items


def process_tokens(items, line_no, tokens):
    """
    Process tokens from a line, appending valid (line_no, integer) to items.
    """
    for token in tokens:
        num = parse_int_token(token)
        if num is None:
            print(
                f"[ERROR] Invalid token at line {line_no}: '{token}'",
                file=sys.stderr,
            )
            items.append((line_no, token))
        else:
            items.append((line_no, num))


def write_results(path, content):
    """Write content to a file."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        print(f"[ERROR] Could not write results file: {exc}", file=sys.stderr)


# Headers
H_LINE = "Line"
H_DEC = "Decimal"
H_BIN = "Binary"
H_HEX = "Hex"


def build_aligned_table(rows, elapsed_seconds, input_path):
    """
    Build an aligned text table for the given rows.

    Args:
        rows (list[tuple[str, str, str, str]]):
            Each tuple is (line_str, decimal_str, bin_str, hex_str)
        elapsed_seconds (float): total elapsed time to print at the end.
        input_path (str): path to the input file.

    Returns:
        str: the full table ready to print/write.
    """
    # Compute max widths per column including headers
    line_width = len(H_LINE)
    dec_width = len(H_DEC)
    bin_width = len(H_BIN)
    hex_width = len(H_HEX)

    for line_str, dec_str, bin_str, hex_str in rows:
        line_width = max(line_width, len(line_str))
        dec_width = max(dec_width, len(dec_str))
        bin_width = max(bin_width, len(bin_str))
        hex_width = max(hex_width, len(hex_str))

    # Small padding between columns
    sep = "  |  "

    # Build header line and separator
    header = (
        H_LINE.rjust(line_width)
        + sep
        + H_DEC.rjust(dec_width)
        + sep
        + H_BIN.rjust(bin_width)
        + sep
        + H_HEX.rjust(hex_width)
    )
    rule = (
        "-" * line_width
        + sep.replace("|", "+").replace(" ", "-")
        + "-" * dec_width
        + sep.replace("|", "+").replace(" ", "-")
        + "-" * bin_width
        + sep.replace("|", "+").replace(" ", "-")
        + "-" * hex_width
    )

    lines = []
    line_header = f"=== {input_path} Conversions (Line, Decimal → Binary, Hex) ==="
    lines.append(line_header)
    lines.append("")
    lines.append(header)
    lines.append(rule)

    for line_str, dec_str, bin_str, hex_str in rows:
        line = (
            line_str.rjust(line_width)
            + sep
            + dec_str.rjust(dec_width)
            + sep
            + bin_str.rjust(bin_width)
            + sep
            + hex_str.rjust(hex_width)
        )
        lines.append(line)

    lines.append("")
    lines.append(f"Total valid items: {len(rows)}")
    lines.append(f"Elapsed Time (seconds): {elapsed_seconds:.6f}")

    return "\n".join(lines) + "\n"


def prepare_rows(line_value_pairs):
    """
    Convert (line_no, value) to table rows using basic algorithms.
    For negatives:
      - BIN: two's complement, 10 bits (e.g., -39 -> 1111011001)
      - HEX: two's complement, 10 hex digits (40 bits) (e.g., -39 -> FFFFFFFFD9)
    For non-negatives:
      - BIN/HEX: standard conversion without sign/padding.
    Returns:
        list[tuple[str, str, str, str]]
    """
    rows = []
    for line_no, value in line_value_pairs:
        line_str = str(line_no)
        dec_str = str(value)

        if value is None or not isinstance(value, int):
            bin_str = "#VALUE!"
            hex_str = "#VALUE!"
        else:
            if value < 0:
                bin_str = twos_complement_bin(value, bits=10)
                hex_str = twos_complement_hex(value, hex_width=10)
            else:
                bin_str = to_base_string(value, 2)
                hex_str = to_base_string(value, 16)

        rows.append((line_str, dec_str, bin_str, hex_str))
    return rows


def main():
    """
    Entry point: accept one or multiple input files, convert integers to bases
    per file, and print/write one combined report at the end.
    """
    if len(sys.argv) < 2:
        print(
            "Usage:\n  python convertNumbers.py file1.txt [file2.txt ... fileN.txt]",
            file=sys.stderr,
        )
        sys.exit(2)

    input_paths = sys.argv[1:]
    all_sections = []
    overall_start = time.perf_counter()

    for input_path in input_paths:
        start_time = time.perf_counter()

        try:
            line_value_pairs = parse_integers_from_file(input_path)
        except OSError as exc:
            print(f"[FATAL] Cannot read file '{input_path}': {exc}", file=sys.stderr)
            # continue with the next file instead of aborting the batch
            continue

        if len(line_value_pairs) == 0:
            elapsed = time.perf_counter() - start_time
            lines = [
                f"=== {input_path} Number Base Conversions (Line, Decimal → Binary, Hex) ===",
                "",
                "Total valid items: 0",
                "(no valid integers to convert)",
                "",
                f"Elapsed Time (seconds): {elapsed:.6f}",
                "",
            ]
            section = "\n".join(lines)
            print(section)
            all_sections.append(section)
            continue

        rows = prepare_rows(line_value_pairs)
        elapsed = time.perf_counter() - start_time

        # Build the section for this input file (keeps your table format)
        section = build_aligned_table(rows, elapsed, input_path)
        print(section)
        all_sections.append(section)

    if not all_sections:
        print("[ERROR] No valid inputs were processed.", file=sys.stderr)
        sys.exit(1)

    # Optional batch summary footer
    overall_elapsed = time.perf_counter() - overall_start
    footer = (
        "\n=== Batch Summary ===\n"
        f"Files processed: {len(all_sections)}\n"
        f"Total elapsed time (seconds): {overall_elapsed:.6f}\n"
    )

    # Join all file sections into a single combined report
    combined_report = "\n".join(all_sections) + footer

    # Single write at the end
    write_results("results/ConvertionResults.txt", combined_report)


if __name__ == "__main__":
    main()
