"""
datatoolkit
-----------
A small, dependency-free toolkit of pure functions for string manipulation,
lightweight data parsing, basic statistics, and simple format validation.

Every function here is deterministic and side-effect free (no file or
network I/O), which is what makes the module straightforward to unit test:
given the same input, each function always returns the same output.
"""

import csv
import io
import re
import statistics


# ---------------------------------------------------------------------------
# String manipulation
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text):
    """Collapse any run of whitespace into a single space and trim the ends."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def to_title_case(text, exceptions=None):
    """Title-case a string, keeping words in `exceptions` lowercase.

    The first word is always capitalized even if it appears in
    `exceptions` (e.g. "of mice and men" -> "Of Mice and Men").
    """
    exceptions = exceptions or set()
    words = text.split()
    result = []
    for i, word in enumerate(words):
        if i > 0 and word.lower() in exceptions:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return " ".join(result)


_PALINDROME_STRIP_RE = re.compile(r"[^a-z0-9]")


def is_palindrome(text):
    """Return True if `text` is a palindrome, ignoring case/spaces/punctuation."""
    cleaned = _PALINDROME_STRIP_RE.sub("", text.lower())
    return cleaned == cleaned[::-1]


def truncate(text, length, suffix="..."):
    """Truncate `text` to at most `length` characters, appending `suffix`.

    Raises ValueError if `length` is too short to even fit the suffix.
    """
    if length < len(suffix):
        raise ValueError(
            f"length ({length}) must be at least as long as suffix ({len(suffix)!r})"
        )
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


# ---------------------------------------------------------------------------
# Data parsing
# ---------------------------------------------------------------------------

def parse_csv_line(line, delimiter=","):
    """Parse a single CSV-style line into a list of trimmed fields.

    Supports quoted fields that contain the delimiter, e.g.
    parse_csv_line('a,"b,c",d') -> ["a", "b,c", "d"].
    """
    reader = csv.reader(io.StringIO(line), delimiter=delimiter, skipinitialspace=True)
    row = next(reader, [""])
    return [field.strip() for field in row]


def parse_key_value_pairs(text, pair_sep=";", kv_sep="="):
    """Parse "a=1;b=2" into {"a": "1", "b": "2"}.

    Raises ValueError if any non-empty segment doesn't contain `kv_sep`.
    """
    result = {}
    if not text.strip():
        return result

    for segment in text.split(pair_sep):
        segment = segment.strip()
        if not segment:
            continue
        if kv_sep not in segment:
            raise ValueError(f"Malformed key-value pair: {segment!r}")
        key, value = segment.split(kv_sep, 1)
        result[key.strip()] = value.strip()
    return result


def parse_int_safe(value, default=None):
    """Parse `value` as an int, returning `default` instead of raising."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def parse_float_safe(value, default=None):
    """Parse `value` as a float, returning `default` instead of raising."""
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Math / statistics
# ---------------------------------------------------------------------------

def mean(numbers):
    """Arithmetic mean of a non-empty sequence of numbers."""
    if not numbers:
        raise ValueError("mean() requires at least one number")
    return sum(numbers) / len(numbers)


def median(numbers):
    """Median of a non-empty sequence of numbers."""
    if not numbers:
        raise ValueError("median() requires at least one number")
    return statistics.median(numbers)


def stdev(numbers):
    """Sample standard deviation; requires at least two numbers."""
    if len(numbers) < 2:
        raise ValueError("stdev() requires at least two numbers")
    return statistics.stdev(numbers)


def clamp(value, min_value, max_value):
    """Clamp `value` into the inclusive range [min_value, max_value]."""
    if min_value > max_value:
        raise ValueError(
            f"min_value ({min_value}) must not exceed max_value ({max_value})"
        )
    return max(min_value, min(value, max_value))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_PHONE_RE = re.compile(r"^(\+\d{1,3}[\s-]?)?(\d[\s-]?){10}$")


def is_valid_email(text):
    """Lightweight structural email check (not full RFC 5322)."""
    return bool(_EMAIL_RE.match(text))


def is_valid_phone(text):
    """Lightweight phone check: optional country code + 10 digits.

    Accepts spaces or dashes as separators between digits.
    """
    return bool(_PHONE_RE.match(text))


# ---------------------------------------------------------------------------
# Integration-level function: composes parsing + safe-parsing + statistics
# ---------------------------------------------------------------------------

def parse_and_summarize_csv(text, numeric_columns):
    """Parse a CSV-like block of text and summarize the requested columns.

    `text` must have a header row followed by at least one data row.
    For each name in `numeric_columns`, invalid or missing values in that
    column are skipped (not fatal) using parse_float_safe, and the
    remaining values are summarized with mean/median/stdev/count.

    Raises:
        ValueError: if there are no data rows at all.
        KeyError: if a requested column name isn't in the header.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError("Expected a header row plus at least one data row")

    header = parse_csv_line(lines[0])
    data_rows = [parse_csv_line(line) for line in lines[1:]]

    for column in numeric_columns:
        if column not in header:
            raise KeyError(f"Unknown column: {column!r}")

    summaries = {}
    for column in numeric_columns:
        col_index = header.index(column)
        values = []
        for row in data_rows:
            raw = row[col_index] if col_index < len(row) else None
            parsed = parse_float_safe(raw)
            if parsed is not None:
                values.append(parsed)

        summaries[column] = {
            "count": len(values),
            "mean": mean(values) if values else None,
            "median": median(values) if values else None,
            "stdev": stdev(values) if len(values) >= 2 else None,
        }

    return summaries
