"""
Unit tests for datatoolkit.

Written BEFORE datatoolkit.py exists (TDD red phase). Each test describes
one specific behavior the module must satisfy. Run with:

    python3 -m pytest test_unit_datatoolkit.py -v
"""

import pytest
import datatoolkit as dt


# ---------------------------------------------------------------------------
# String manipulation
# ---------------------------------------------------------------------------

class TestNormalizeWhitespace:
    def test_collapses_multiple_spaces(self):
        assert dt.normalize_whitespace("a    b") == "a b"

    def test_collapses_tabs_and_newlines(self):
        assert dt.normalize_whitespace("a\t\tb\n\nc") == "a b c"

    def test_strips_leading_and_trailing_whitespace(self):
        assert dt.normalize_whitespace("   hello world   ") == "hello world"

    def test_empty_string_stays_empty(self):
        assert dt.normalize_whitespace("") == ""

    def test_already_normalized_string_is_unchanged(self):
        assert dt.normalize_whitespace("hello world") == "hello world"


class TestToTitleCase:
    def test_basic_sentence(self):
        assert dt.to_title_case("the quick brown fox") == "The Quick Brown Fox"

    def test_exceptions_stay_lowercase_mid_sentence(self):
        assert dt.to_title_case(
            "lord of the rings", exceptions={"of", "the"}
        ) == "Lord of the Rings"

    def test_first_word_capitalized_even_if_in_exceptions(self):
        assert dt.to_title_case(
            "of mice and men", exceptions={"of", "and"}
        ) == "Of Mice and Men"

    def test_empty_string_returns_empty(self):
        assert dt.to_title_case("") == ""

    def test_no_exceptions_provided_title_cases_everything(self):
        assert dt.to_title_case("game of thrones") == "Game Of Thrones"


class TestIsPalindrome:
    def test_simple_word_palindrome(self):
        assert dt.is_palindrome("racecar") is True

    def test_phrase_palindrome_ignores_case_and_spaces(self):
        assert dt.is_palindrome("A man a plan a canal Panama") is True

    def test_non_palindrome(self):
        assert dt.is_palindrome("hello") is False

    def test_empty_string_is_trivially_palindrome(self):
        assert dt.is_palindrome("") is True

    def test_single_character_is_palindrome(self):
        assert dt.is_palindrome("x") is True

    def test_ignores_punctuation(self):
        assert dt.is_palindrome("Was it a car or a cat I saw?") is True


class TestTruncate:
    def test_short_text_is_unchanged(self):
        assert dt.truncate("hello", 10) == "hello"

    def test_text_at_exact_length_is_unchanged(self):
        assert dt.truncate("hello", 5) == "hello"

    def test_long_text_is_truncated_with_suffix(self):
        assert dt.truncate("hello world", 8) == "hello..."

    def test_custom_suffix(self):
        assert dt.truncate("hello world", 7, suffix=">>") == "hello>>"

    def test_length_shorter_than_suffix_raises_value_error(self):
        with pytest.raises(ValueError):
            dt.truncate("hello world", 2, suffix="...")


# ---------------------------------------------------------------------------
# Data parsing
# ---------------------------------------------------------------------------

class TestParseCsvLine:
    def test_simple_comma_split(self):
        assert dt.parse_csv_line("a,b,c") == ["a", "b", "c"]

    def test_trims_surrounding_whitespace(self):
        assert dt.parse_csv_line(" a , b , c ") == ["a", "b", "c"]

    def test_quoted_field_containing_delimiter(self):
        assert dt.parse_csv_line('a,"b,c",d') == ["a", "b,c", "d"]

    def test_custom_delimiter(self):
        assert dt.parse_csv_line("a;b;c", delimiter=";") == ["a", "b", "c"]

    def test_empty_line_returns_single_empty_field(self):
        assert dt.parse_csv_line("") == [""]


class TestParseKeyValuePairs:
    def test_basic_pairs(self):
        assert dt.parse_key_value_pairs("a=1;b=2") == {"a": "1", "b": "2"}

    def test_ignores_surrounding_whitespace(self):
        assert dt.parse_key_value_pairs(" a = 1 ; b = 2 ") == {"a": "1", "b": "2"}

    def test_custom_separators(self):
        assert dt.parse_key_value_pairs("a:1,b:2", pair_sep=",", kv_sep=":") == \
            {"a": "1", "b": "2"}

    def test_empty_text_returns_empty_dict(self):
        assert dt.parse_key_value_pairs("") == {}

    def test_malformed_pair_raises_value_error(self):
        with pytest.raises(ValueError):
            dt.parse_key_value_pairs("a=1;bad;c=3")

    def test_empty_segment_from_repeated_separator_is_skipped(self):
        assert dt.parse_key_value_pairs("a=1;;b=2") == {"a": "1", "b": "2"}


class TestParseIntSafe:
    def test_valid_int_string(self):
        assert dt.parse_int_safe("42") == 42

    def test_invalid_string_returns_default(self):
        assert dt.parse_int_safe("abc", default=0) == 0

    def test_float_string_returns_default(self):
        assert dt.parse_int_safe("3.5", default=-1) == -1

    def test_none_input_returns_default(self):
        assert dt.parse_int_safe(None, default=99) == 99

    def test_default_of_default_is_none(self):
        assert dt.parse_int_safe("nope") is None


class TestParseFloatSafe:
    def test_valid_float_string(self):
        assert dt.parse_float_safe("3.14") == pytest.approx(3.14)

    def test_valid_int_string_parses_as_float(self):
        assert dt.parse_float_safe("42") == pytest.approx(42.0)

    def test_invalid_string_returns_default(self):
        assert dt.parse_float_safe("abc", default=0.0) == 0.0

    def test_none_input_returns_default(self):
        assert dt.parse_float_safe(None, default=1.5) == 1.5


# ---------------------------------------------------------------------------
# Math / statistics
# ---------------------------------------------------------------------------

class TestMean:
    def test_typical_values(self):
        assert dt.mean([1, 2, 3, 4]) == pytest.approx(2.5)

    def test_single_value(self):
        assert dt.mean([7]) == 7.0

    def test_empty_list_raises_value_error(self):
        with pytest.raises(ValueError):
            dt.mean([])


class TestMedian:
    def test_odd_length_list(self):
        assert dt.median([5, 1, 3]) == 3

    def test_even_length_list_averages_middle_two(self):
        assert dt.median([1, 2, 3, 4]) == pytest.approx(2.5)

    def test_unsorted_input_is_handled(self):
        assert dt.median([9, 1, 5, 3, 7]) == 5

    def test_empty_list_raises_value_error(self):
        with pytest.raises(ValueError):
            dt.median([])


class TestStdev:
    def test_typical_values(self):
        # sample stdev of [2, 4, 4, 4, 5, 5, 7, 9] is 2.13809...
        assert dt.stdev([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2.1381, rel=1e-3)

    def test_single_value_raises_value_error(self):
        with pytest.raises(ValueError):
            dt.stdev([5])

    def test_empty_list_raises_value_error(self):
        with pytest.raises(ValueError):
            dt.stdev([])


class TestClamp:
    def test_value_within_bounds_is_unchanged(self):
        assert dt.clamp(5, 0, 10) == 5

    def test_value_below_minimum_is_clamped_up(self):
        assert dt.clamp(-5, 0, 10) == 0

    def test_value_above_maximum_is_clamped_down(self):
        assert dt.clamp(15, 0, 10) == 10

    def test_min_greater_than_max_raises_value_error(self):
        with pytest.raises(ValueError):
            dt.clamp(5, 10, 0)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestIsValidEmail:
    def test_simple_valid_email(self):
        assert dt.is_valid_email("user@example.com") is True

    def test_valid_email_with_subdomain_and_plus(self):
        assert dt.is_valid_email("user+tag@mail.example.co.in") is True

    def test_missing_at_symbol_is_invalid(self):
        assert dt.is_valid_email("userexample.com") is False

    def test_missing_domain_dot_is_invalid(self):
        assert dt.is_valid_email("user@examplecom") is False

    def test_spaces_are_invalid(self):
        assert dt.is_valid_email("user @example.com") is False


class TestIsValidPhone:
    def test_plain_ten_digits(self):
        assert dt.is_valid_phone("9876543210") is True

    def test_with_dashes(self):
        assert dt.is_valid_phone("987-654-3210") is True

    def test_with_country_code(self):
        assert dt.is_valid_phone("+91 9876543210") is True

    def test_too_short_is_invalid(self):
        assert dt.is_valid_phone("12345") is False

    def test_letters_are_invalid(self):
        assert dt.is_valid_phone("98765abcde") is False
