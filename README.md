# datatoolkit — Test Documentation

A small, dependency-free Python module of pure functions for string
manipulation, lightweight data parsing, basic statistics, and simple format
validation — built test-first (TDD) with a full unit + integration test
suite.

## Contents

- `datatoolkit.py` — the module
- `test_unit_datatoolkit.py` — 65 unit tests (one function at a time)
- `test_integration_datatoolkit.py` — 10 integration tests (functions working together)
- `architecture_diagram.png` — module structure and test coverage map
- `Week3_Testing_Report.docx` — full write-up of methodology, TDD process, and reasoning

## How to run the tests

Requires only `pytest` (no other third-party dependencies):

```bash
pip install pytest
python3 -m pytest -v
```

To also see coverage (requires `pytest-cov`):

```bash
pip install pytest-cov
python3 -m pytest --cov=datatoolkit --cov-report=term-missing
```

Current status: **75 tests passing, 100% line coverage** of `datatoolkit.py`.

To run only unit tests, or only integration tests:

```bash
python3 -m pytest test_unit_datatoolkit.py -v
python3 -m pytest test_integration_datatoolkit.py -v
```

## Development approach: TDD (tests written first)

For every function, the test file was written before the corresponding
function existed. The first run of the suite failed with
`ModuleNotFoundError: No module named 'datatoolkit'` — genuine proof that no
implementation existed yet. Functions were then implemented to satisfy the
tests (red → green), and two of those cycles are deliberately preserved and
documented in the accompanying report as realistic examples: a first-draft
`to_title_case()` that forgot to always capitalize the first word, and a
first-draft `parse_and_summarize_csv()` that used a raw `float()` conversion
instead of a safe one and crashed on the first bad row. Both are shown
failing, then fixed, in the report.

## Why unit tests AND integration tests

The module has one function, `parse_and_summarize_csv()`, that composes
several of the other functions together (`parse_csv_line`, `parse_float_safe`,
`mean`, `median`, `stdev`). Unit tests confirm each of those pieces is
correct in isolation. Integration tests confirm they still behave correctly
*when combined* — which matters because a perfectly correct
`parse_float_safe()` and a perfectly correct `mean()` can still be wired
together incorrectly (e.g. forgetting to filter out `None` values before
averaging). That exact mistake is reproduced and caught in
`test_malformed_numeric_value_is_skipped_not_fatal`.

## Test case reference

Each row explains what a test class covers and why that case was chosen.

### String manipulation

| Test class | Covers | Why this case matters |
|---|---|---|
| `TestNormalizeWhitespace` | Collapsing runs of spaces/tabs/newlines; trimming ends; empty input; already-clean input | Text from user input or files rarely has "clean" single-space formatting — this is the most common pre-processing step before any other string function runs |
| `TestToTitleCase` | Basic title-casing; lowercase exceptions (e.g. "of", "the"); first word always capitalized even if it's an exception word; empty input | The "first word" rule is the one beginners forget, so it gets its own explicit test rather than being assumed to work as a side effect of the exceptions test |
| `TestIsPalindrome` | Simple word, multi-word phrase, non-palindrome, empty string, single character, punctuation | Empty string and single character are the classic "boundary" cases for any symmetry check — if the function isn't tested there, an off-by-one in the comparison can hide indefinitely |
| `TestTruncate` | Text shorter than limit, text at exact limit, text longer than limit, custom suffix, limit shorter than the suffix itself | The "limit shorter than suffix" case is an error condition, not just an edge case — it's the one scenario where the function genuinely cannot do what was asked, so it must raise rather than return a wrong answer |

### Data parsing

| Test class | Covers | Why this case matters |
|---|---|---|
| `TestParseCsvLine` | Plain comma split, surrounding whitespace, quoted field containing the delimiter, custom delimiter, empty line | The quoted-field case is the entire reason this function exists instead of a one-line `text.split(",")` — real CSV data routinely has commas inside quoted text fields |
| `TestParseKeyValuePairs` | Basic pairs, surrounding whitespace, custom separators, empty text, a malformed segment (no `=`), a doubled separator producing an empty segment | Malformed input is treated as an error (raises `ValueError`) rather than silently dropped, because silently dropping a bad config/setting is a worse failure mode than a loud one |
| `TestParseIntSafe` / `TestParseFloatSafe` | Valid numeric strings, non-numeric strings, `None` input, a float-formatted string passed to the int parser | These exist specifically so that "user-typed" values (which are always strings, and are never guaranteed to be well-formed) can be converted without a `try/except` at every call site |

### Math / statistics

| Test class | Covers | Why this case matters |
|---|---|---|
| `TestMean` | Typical values, a single value, an empty list | An empty list is a `ZeroDivisionError` waiting to happen if unguarded — it's tested explicitly to confirm it instead raises a clear `ValueError` |
| `TestMedian` | Odd-length list, even-length list (average of two middle values), unsorted input, empty list | Even-length lists are the case most likely to be implemented wrong (forgetting to average the two middle values instead of just picking one) |
| `TestStdev` | A typical dataset (checked against a hand-verified value), a single value, an empty list | Standard deviation is mathematically undefined for fewer than two data points, so both the 0-item and 1-item cases are tested as explicit error conditions |
| `TestClamp` | Value inside range, below minimum, above maximum, `min > max` (invalid range) | An inverted range (`min > max`) is a caller mistake that should fail loudly rather than silently returning a nonsensical clamped value |

### Validation

| Test class | Covers | Why this case matters |
|---|---|---|
| `TestIsValidEmail` | A simple valid address, a valid address with a subdomain and `+` tag, missing `@`, missing domain dot, embedded spaces | These are structural checks, not full RFC 5322 validation — the tests are scoped to match what the function actually promises to check, rather than implying it catches every possible malformed email |
| `TestIsValidPhone` | Plain 10 digits, dash-separated, with a country code, too short, containing letters | Covers the three realistic input shapes a user might type (plain, dashed, with country code) plus two clear rejection cases |

### Integration (`parse_and_summarize_csv`)

| Test class | Covers | Why this case matters |
|---|---|---|
| `TestParseAndSummarizeCsvHappyPath` | Correct column selection, mean/median/stdev correctness against a hand-checked dataset, row count reporting | Confirms the "everything works" path is verified against manually computed numbers, not just "it didn't crash" |
| `TestParseAndSummarizeCsvWithMessyData` | A malformed value in one row, a quoted text field with a comma in an unrelated column, header-only input, an unknown requested column, multiple numeric columns summarized independently, a column where every value is invalid | This is where real-world messiness lives — the happy path is necessary but not sufficient; these six cases are what actually justify calling this an integration test rather than a second unit test |

## Design notes / known limitations

- `is_valid_email` and `is_valid_phone` are intentionally lightweight
  structural checks, not full format-specification validators. This is
  documented in their docstrings and reflected in the test scope above.
- `parse_and_summarize_csv` skips invalid numeric values rather than failing
  the whole summary, which was a deliberate design decision verified by the
  `test_malformed_numeric_value_is_skipped_not_fatal` integration test — the
  report explains the earlier draft that got this wrong.
