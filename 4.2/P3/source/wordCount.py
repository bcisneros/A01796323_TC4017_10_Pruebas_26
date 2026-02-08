#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
wordCount.py

Command-line program that reads a file containing words (space-separated)
and computes the frequency of each distinct word using only basic algorithms
(no regex, no collections.Counter, no sorted).

It prints results to console and writes them to 'WordCountResults.txt',
with aligned columns for readability.

Ordering: by frequency DESC, then by word ASC (alphabetical).

Invalid tokens are reported to the console (stderr), and execution continues.

Usage:
    python wordCount.py fileWithData.txt
"""

import sys
import time


def to_lower(s):
    """Return a lowercase version of the string (basic normalization)."""
    return s.lower()


def is_alpha_numeric(c):
    """Return True if character is alphanumeric (Unicode-aware)."""
    return c.isalnum()


def has_alpha(s):
    """Return True if the string contains at least one alphabetic letter."""
    for ch in s:
        if ch.isalpha():
            return True
    return False


def strip_non_alpha_numeric_edges(token):
    """
    Remove leading/trailing non-alphanumeric characters from token.
    Keeps internal punctuation as-is.
    Example: '"Hola,"' -> 'Hola'
    """
    if token == "":
        return ""

    start = 0
    end = len(token) - 1

    # Move start forward while non-alphanumeric
    while start <= end and not is_alpha_numeric(token[start]):
        start += 1

    # Move end backward while non-alphanumeric
    while end >= start and not is_alpha_numeric(token[end]):
        end -= 1

    if start > end:
        return ""

    return token[start: end + 1]


def normalize_word(token):
    """
    Normalize a token into a comparable 'word':
      - trim non-alphanumeric characters on edges,
      - lowercase the result.
    Consider invalid if empty after trimming or has no alphabetic letter.
    """
    if token is None:
        return None

    trimmed = strip_non_alpha_numeric_edges(token.strip())
    if trimmed == "":
        return None

    lowered = to_lower(trimmed)

    if not has_alpha(lowered):
        # No alphabetic letter → not considered a 'word' for this task.
        return None

    return lowered


def parse_words_from_file(path):
    """
    Parse words from text file. Tokens are split by whitespace.
    Invalid tokens are reported to stderr and ignored.

    Returns:
        list[str]: list of valid normalized words.
    """
    words = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line_no, raw in enumerate(fh, start=1):
                # Split by whitespace
                for token in raw.split():
                    w = normalize_word(token)
                    if w is None:
                        report_invalid_token(line_no, token)
                    else:
                        words.append(w)
    except FileNotFoundError:
        print(f"[FATAL] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"[FATAL] Cannot read file '{path}': {exc}", file=sys.stderr)
        sys.exit(1)

    return words


def report_invalid_token(line_no, token):
    """Report an invalid token to stderr."""
    print(
        f"[ERROR] Invalid token at line {line_no}: '{token}'",
        file=sys.stderr,
    )


def count_frequencies(words):
    """
    Count frequencies using a basic dictionary and loops.

    Returns:
        dict[str, int]
    """
    freq = {}
    for w in words:
        if w in freq:
            freq[w] += 1
        else:
            freq[w] = 1
    return freq


# ===== Merge sort personalizado: (word, count) con orden: count DESC, word ASC


def merge_pairs(left, right):
    """
    Merge step for merge sort on list of (word, count) tuples with order:
      - Primary: count DESC
      - Secondary: word ASC (lexicographically)
    """
    merged = []
    i = 0
    j = 0
    len_left = len(left)
    len_right = len(right)

    while i < len_left and j < len_right:
        w1, c1 = left[i]
        w2, c2 = right[j]

        # Compare by count DESC
        if c1 > c2:
            merged.append(left[i])
            i += 1
        elif c1 < c2:
            merged.append(right[j])
            j += 1
        else:
            # counts equal → word ASC
            if w1 <= w2:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

    while i < len_left:
        merged.append(left[i])
        i += 1
    while j < len_right:
        merged.append(right[j])
        j += 1

    return merged


def merge_sort_pairs(arr):
    """
    Merge sort for (word, count) tuples using the custom order.
    Returns a new sorted list.
    """
    n = len(arr)
    if n <= 1:
        return arr[:]
    mid = n // 2
    left_sorted = merge_sort_pairs(arr[:mid])
    right_sorted = merge_sort_pairs(arr[mid:])
    return merge_pairs(left_sorted, right_sorted)


def write_results(path, content):
    """Write content to a file."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        print(f"[ERROR] Could not write results file: {exc}", file=sys.stderr)


def build_aligned_table(pairs, total_valid, elapsed_seconds):
    """
    Build an aligned text table for (word, count) pairs.

    Args:
        pairs (list[tuple[str, int]]): sorted list of (word, count)
        total_valid (int): total number of valid words processed
        elapsed_seconds (float): total elapsed time

    Returns:
        str: full table text ready to print/write.
    """
    header_word = "Word"
    header_count = "Frequency"

    word_width = len(header_word)
    count_width = len(header_count)

    # Compute max widths
    for w, c in pairs:
        word_width = max(word_width, len(w))
        count_width = max(count_width, len(str(c)))

    sep = "  |  "
    left = header_word.ljust(word_width)
    header = left + sep + header_count.rjust(count_width)
    new_sep = sep.replace("|", "+").replace(" ", "-")
    rule = "-" * word_width + new_sep + "-" * count_width

    lines = []
    lines.append("")
    lines.append(header)
    lines.append(rule)

    for w, c in pairs:
        line = w.ljust(word_width) + sep + str(c).rjust(count_width)
        lines.append(line)

    lines.append("")
    lines.append(f"Total valid words: {total_valid}")
    lines.append(f"Distinct words: {len(pairs)}")
    lines.append(f"Elapsed Time (seconds): {elapsed_seconds:.6f}")
    lines.append("")

    return "\n".join(lines)

def build_file_section(input_path, words, elapsed_seconds):
    """
    Build the text section for one file: header + aligned table + totals.
    """
    # Frequency dictionary
    freq = count_frequencies(words)
    # Build (word, count) tuples
    pairs = []
    for w, c in freq.items():
        pairs.append((w, c))
    # Sort: count DESC, word ASC
    sorted_pairs = merge_sort_pairs(pairs)

    section_body = build_aligned_table(sorted_pairs, len(words), elapsed_seconds)

    # Add a file-specific title
    header = f"=== {input_path} — Word Count (Distinct Words & Frequencies) ===\n"
    return header + section_body

def main():
    """
    Entry point: accept one or multiple input files, parse words, count, sort,
    print aligned results per file, and write one combined report at the end.
    """
    if len(sys.argv) < 2:
        print(
            "Usage:\n  python wordCount.py file1.txt [file2.txt ... fileN.txt]",
            file=sys.stderr,
        )
        sys.exit(2)

    input_paths = sys.argv[1:]
    all_sections = []
    overall_start = time.perf_counter()

    for input_path in input_paths:
        start_time = time.perf_counter()
        try:
            words = parse_words_from_file(input_path)
        except SystemExit:
            # parse_words_from_file calls sys.exit(1) on fatal; to keep the batch running:
            # re-raise would stop the entire batch; instead, just continue
            # (If you prefer to enforce an exit on fatal, remove this block.)
            continue
        except Exception as exc:  # extra safety
            print(f"[FATAL] Unexpected error reading '{input_path}': {exc}", file=sys.stderr)
            continue

        elapsed = time.perf_counter() - start_time

        # If no valid words, print an empty section with totals = 0
        if len(words) == 0:
            lines = [
                f"=== {input_path} — Word Count (Distinct Words & Frequencies) ===",
                "",
                "Word             |  Frequency",
                "-----------------+-----------",
                "",
                "Total valid words: 0",
                "Distinct words: 0",
                f"Elapsed Time (seconds): {elapsed:.6f}",
                "",
            ]
            section = "\n".join(lines)
        else:
            section = build_file_section(input_path, words, elapsed)

        print(section)
        all_sections.append(section)

    if not all_sections:
        print("[ERROR] No valid inputs were processed.", file=sys.stderr)
        sys.exit(1)

    overall_elapsed = time.perf_counter() - overall_start
    footer = (
        "\n=== Batch Summary ===\n"
        f"Files processed: {len(all_sections)}\n"
        f"Total elapsed time (seconds): {overall_elapsed:.6f}\n"
    )

    combined_report = "\n".join(all_sections) + footer

    try:
        import os
        os.makedirs("results", exist_ok=True)
    except Exception as exc:
        print(f"[WARN] Could not ensure 'results/' directory: {exc}", file=sys.stderr)

    write_results("results/WordCountResults.txt", combined_report)


if __name__ == "__main__":
    main()
