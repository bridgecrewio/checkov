"""Tests for regex / regexall evaluation with RE2 engine.

The ``regex()`` and ``regexall()`` helpers in ``safe_eval_functions`` use
Google's RE2 engine (via ``google-re2``) which uses a linear-time matching
algorithm.  This matches the behaviour of Terraform's own regex engine
(Go's ``regexp`` package is also RE2-based).

These tests verify that:
1. Normal regex patterns continue to work correctly.
2. Complex patterns with nested quantifiers complete in bounded time.
"""

from __future__ import annotations

import time

import pytest

from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import evaluate_terraform
import checkov.terraform.graph_builder.variable_rendering.safe_eval_functions as safe_eval_mod


# ---------------------------------------------------------------------------
# Normal (non-pathological) patterns must still work
# ---------------------------------------------------------------------------

class TestRegexNormalBehaviour:
    """Verify that the RE2 engine does not break ordinary regex calls."""

    def test_regex_simple_match(self) -> None:
        assert safe_eval_mod.regex("[a-z]+", "53453453.345345aaabbbccc23454") == "aaabbbccc"

    def test_regex_no_match(self) -> None:
        assert safe_eval_mod.regex("[a-z]+", "53453453.34534523454") == ""

    def test_regex_named_groups(self) -> None:
        result = safe_eval_mod.regex(
            "^(?:(?P<scheme>[^:/?#]+):)?(?://(?P<authority>[^/?#]*))?",
            "https://terraform.io/docs/",
        )
        assert result == {"authority": "terraform.io", "scheme": "https"}

    def test_regex_unnamed_groups(self) -> None:
        result = safe_eval_mod.regex(r"(\d\d\d\d)-(\d\d)-(\d\d)", "2019-02-01")
        assert result == ["2019", "02", "01"]

    def test_regexall_multiple_matches(self) -> None:
        assert safe_eval_mod.regexall("[a-z]+", "1234abcd5678efgh9") == ["abcd", "efgh"]

    def test_regexall_no_match(self) -> None:
        assert safe_eval_mod.regexall("[a-z]+", "123456789") == []


# ---------------------------------------------------------------------------
# Complex patterns with nested quantifiers must complete in bounded time
# ---------------------------------------------------------------------------

# Pattern with nested quantifiers and a non-matching input.
_COMPLEX_PATTERN = "(a+)+$"
# 30 'a's followed by '!' — this input does not match the pattern.
# With Python's stdlib re engine this would take exponential time;
# RE2 handles it in linear time.
_COMPLEX_INPUT = "a" * 30 + "!"


class TestRegexRe2Performance:
    """Patterns with nested quantifiers must complete in bounded time
    when RE2 is used as the regex engine."""

    def test_regex_nested_quantifier_completes_fast(self) -> None:
        """``regex()`` with a nested-quantifier pattern must complete
        in well under a second with RE2."""
        start = time.monotonic()
        result = safe_eval_mod.regex(_COMPLEX_PATTERN, _COMPLEX_INPUT)
        elapsed = time.monotonic() - start
        # RE2 returns empty string (no match) instantly
        assert result == ""
        assert elapsed < 1.0, f"took {elapsed:.2f}s — expected sub-second"

    def test_regexall_nested_quantifier_completes_fast(self) -> None:
        """``regexall()`` with a nested-quantifier pattern must complete
        in well under a second with RE2."""
        start = time.monotonic()
        result = safe_eval_mod.regexall(_COMPLEX_PATTERN, _COMPLEX_INPUT)
        elapsed = time.monotonic() - start
        assert result == []
        assert elapsed < 1.0, f"took {elapsed:.2f}s — expected sub-second"

    def test_evaluate_terraform_regex_nested_quantifier(self) -> None:
        """End-to-end: ``evaluate_terraform`` must handle a nested-quantifier
        ``regex()`` call in bounded time."""
        input_str = f'regex("(a+)+$", "{"a" * 30}!")'
        start = time.monotonic()
        evaluate_terraform(input_str)
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"took {elapsed:.2f}s — expected sub-second with RE2"

    def test_evaluate_terraform_regexall_nested_quantifier(self) -> None:
        """End-to-end: ``evaluate_terraform`` must handle a nested-quantifier
        ``regexall()`` call in bounded time."""
        input_str = f'regexall("(a+)+$", "{"a" * 30}!")'
        start = time.monotonic()
        evaluate_terraform(input_str)
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"took {elapsed:.2f}s — expected sub-second with RE2"
