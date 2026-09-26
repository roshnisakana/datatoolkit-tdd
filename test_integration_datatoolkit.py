"""
Integration tests for datatoolkit.

Unlike the unit tests (test_unit_datatoolkit.py), which each test exactly one
function in isolation, these tests exercise parse_and_summarize_csv(), a
higher-level function that composes several individually-tested pieces
(parse_csv_line, parse_float_safe, mean, median, stdev) into one pipeline.
The goal is to catch problems that only show up when the pieces interact --
for example, a malformed value in one row breaking the whole summary, or a
quoted text field being mistaken for a numeric column.

Run with:  python3 -m pytest test_integration_datatoolkit.py -v
"""

import pytest
import datatoolkit as dt


SAMPLE_CSV = """name,department,score
Amit,Engineering,88
Fatima,Engineering,95
Zoya,Marketing,79
Rahul,Marketing,91
"""


class TestParseAndSummarizeCsvHappyPath:
    def test_returns_stats_for_requested_numeric_column(self):
        result = dt.parse_and_summarize_csv(SAMPLE_CSV, numeric_columns=["score"])
        assert set(result.keys()) == {"score"}

    def test_mean_matches_manual_calculation(self):
        result = dt.parse_and_summarize_csv(SAMPLE_CSV, numeric_columns=["score"])
        # (88 + 95 + 79 + 91) / 4 = 88.25
        assert result["score"]["mean"] == pytest.approx(88.25)

    def test_median_and_stdev_are_present_and_reasonable(self):
        result = dt.parse_and_summarize_csv(SAMPLE_CSV, numeric_columns=["score"])
        assert result["score"]["median"] == pytest.approx(89.5)
        assert result["score"]["stdev"] > 0

    def test_row_count_is_reported(self):
        result = dt.parse_and_summarize_csv(SAMPLE_CSV, numeric_columns=["score"])
        assert result["score"]["count"] == 4


class TestParseAndSummarizeCsvWithMessyData:
    def test_malformed_numeric_value_is_skipped_not_fatal(self):
        messy_csv = """name,score\nAmit,88\nGhost,not-a-number\nFatima,95\n"""
        result = dt.parse_and_summarize_csv(messy_csv, numeric_columns=["score"])
        # Ghost's bad value should be excluded, not crash the whole summary
        assert result["score"]["count"] == 2
        assert result["score"]["mean"] == pytest.approx((88 + 95) / 2)

    def test_quoted_text_field_does_not_break_numeric_parsing(self):
        csv_with_quotes = (
            'name,notes,score\n'
            '"Doe, Jane","likes, commas",90\n'
            'Amit,plain,80\n'
        )
        result = dt.parse_and_summarize_csv(csv_with_quotes, numeric_columns=["score"])
        assert result["score"]["count"] == 2
        assert result["score"]["mean"] == pytest.approx(85.0)

    def test_header_only_csv_raises_value_error(self):
        header_only = "name,score\n"
        with pytest.raises(ValueError):
            dt.parse_and_summarize_csv(header_only, numeric_columns=["score"])

    def test_unknown_numeric_column_raises_key_error(self):
        with pytest.raises(KeyError):
            dt.parse_and_summarize_csv(SAMPLE_CSV, numeric_columns=["salary"])

    def test_multiple_numeric_columns_are_summarized_independently(self):
        two_col_csv = "name,score,rank\nAmit,88,2\nFatima,95,1\n"
        result = dt.parse_and_summarize_csv(two_col_csv, numeric_columns=["score", "rank"])
        assert result["score"]["mean"] == pytest.approx(91.5)
        assert result["rank"]["mean"] == pytest.approx(1.5)

    def test_column_with_no_valid_values_reports_none_not_zero(self):
        # Refactor note: mean/median/stdev must be consistently None (not a
        # misleading 0.0) when a column has zero usable values.
        all_bad_csv = "name,score\nAmit,n/a\nFatima,also-bad\n"
        result = dt.parse_and_summarize_csv(all_bad_csv, numeric_columns=["score"])
        assert result["score"]["count"] == 0
        assert result["score"]["mean"] is None
        assert result["score"]["median"] is None
        assert result["score"]["stdev"] is None
