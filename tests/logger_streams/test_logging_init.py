"""Tests for checkov/logging_init.py LOG_LEVEL handling.

Since logging_init.py executes at module import time, we test the core
logic (basicConfig + setLevel with env-driven LOG_LEVEL) in isolation
to verify that invalid values don't crash the process.
"""
import logging
import os
import subprocess
import sys
import unittest

from checkov.logging_init import FALLBACK_LOG_LEVEL


def _configure_logging(log_level_env: str | None = None) -> int | str:
    """Reproduce the initialization logic from checkov/logging_init.py.

    Returns the effective LOG_LEVEL (str on success, int on fallback).
    """
    raw = (log_level_env if log_level_env is not None
           else logging.getLevelName(FALLBACK_LOG_LEVEL)).upper()
    try:
        logging.basicConfig(level=raw, force=True)
        return raw
    except (ValueError, TypeError):
        logging.basicConfig(level=FALLBACK_LOG_LEVEL, force=True)
        return FALLBACK_LOG_LEVEL


# ---------------------------------------------------------------------------
# Valid Python log levels – these must all succeed
# ---------------------------------------------------------------------------
VALID_PYTHON_LEVELS = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "NOTSET",
]

# ---------------------------------------------------------------------------
# Valid Python aliases – accepted by logging but not the canonical names
# ---------------------------------------------------------------------------
VALID_PYTHON_ALIASES = [
    "FATAL",  # alias for CRITICAL
    "WARN",   # alias for WARNING
]

# ---------------------------------------------------------------------------
# Case-insensitive variants – .upper() should normalise these
# ---------------------------------------------------------------------------
CASE_VARIANTS = [
    ("debug", "DEBUG"),
    ("info", "INFO"),
    ("Warning", "WARNING"),
    ("warning", "WARNING"),
    ("WaRnInG", "WARNING"),
    ("error", "ERROR"),
    ("Error", "ERROR"),
    ("critical", "CRITICAL"),
    ("CrItIcAl", "CRITICAL"),
    ("notset", "NOTSET"),
    ("fatal", "FATAL"),
    ("Warn", "WARN"),
]

# ---------------------------------------------------------------------------
# Invalid / non-Python level strings – must fall back to WARNING
# ---------------------------------------------------------------------------
INVALID_LEVELS = [
    # Common levels from other ecosystems (Java, Rust, syslog, etc.)
    "TRACE",
    "VERBOSE",
    "SEVERE",
    "FINE",
    "FINER",
    "FINEST",
    "OFF",
    "ALL",
    "NOTICE",
    "ALERT",
    "EMERG",
    "EMERGENCY",
    # Misspellings
    "DBUG",
    "DEUBG",
    "DUBUG",
    "INFOO",
    "WARINING",
    "WARNNING",
    "WARING",
    "EROR",
    "ERRROR",
    "CRTICAL",
    "CRITCAL",
    # Garbage
    "",
    "   ",
    "123",
    "NONE",
    "NULL",
    "TRUE",
    "FALSE",
    "YES",
    "NO",
]

ALL_VALID_LEVELS = VALID_PYTHON_LEVELS + VALID_PYTHON_ALIASES


class TestLoggingInitValidLevels(unittest.TestCase):
    """Verify every valid Python log level is accepted without error."""

    def test_valid_levels(self) -> None:
        for level in VALID_PYTHON_LEVELS:
            with self.subTest(level=level):
                result = _configure_logging(level)
                self.assertEqual(result, level)

    def test_valid_aliases(self) -> None:
        for level in VALID_PYTHON_ALIASES:
            with self.subTest(level=level):
                result = _configure_logging(level)
                self.assertEqual(result, level)


class TestLoggingInitCaseInsensitivity(unittest.TestCase):
    """LOG_LEVEL should be case-insensitive thanks to .upper()."""

    def test_case_variants(self) -> None:
        for raw, expected in CASE_VARIANTS:
            with self.subTest(raw=raw):
                result = _configure_logging(raw)
                self.assertEqual(result, expected)


class TestLoggingInitInvalidLevels(unittest.TestCase):
    """Invalid LOG_LEVEL values must not crash; they should fall back."""

    def test_invalid_levels_do_not_crash(self) -> None:
        for level in INVALID_LEVELS:
            with self.subTest(level=level):
                result = _configure_logging(level)
                self.assertEqual(result, FALLBACK_LOG_LEVEL,
                                 f"Expected fallback for invalid level {level!r}")

    def test_none_env_defaults_to_warning(self) -> None:
        result = _configure_logging(None)
        self.assertEqual(result, logging.getLevelName(FALLBACK_LOG_LEVEL))


class TestLoggingInitSetLevel(unittest.TestCase):
    """Verify setLevel behaviour with valid and invalid level strings."""

    def test_setLevel_with_valid_levels(self) -> None:
        handler = logging.StreamHandler()
        for level in ALL_VALID_LEVELS:
            with self.subTest(level=level):
                handler.setLevel(level)  # should not raise

    def test_setLevel_rejects_invalid_levels(self) -> None:
        """setLevel raises ValueError on invalid strings, confirming that
        the fallback in logging_init.py must reassign LOG_LEVEL so that
        downstream setLevel() calls don't crash.
        """
        handler = logging.StreamHandler()
        for level in INVALID_LEVELS:
            if not level.strip():
                continue  # empty/whitespace handled differently
            with self.subTest(level=level):
                with self.assertRaises(ValueError,
                                       msg=f"setLevel({level!r}) should raise ValueError"):
                    handler.setLevel(level.upper())


class TestLoggingInitModuleImport(unittest.TestCase):
    """End-to-end: verify the actual module import doesn't crash.

    Uses subprocess so the module-level code runs fresh in a clean
    Python process. Skipped if checkov dependencies aren't installed.
    """

    def _import_logging_init(self, log_level: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["LOG_LEVEL"] = log_level
        return subprocess.run(
            [sys.executable, "-c", "import checkov.logging_init"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_valid_levels_import_succeeds(self) -> None:
        for level in ALL_VALID_LEVELS:
            with self.subTest(level=level):
                result = self._import_logging_init(level)
                self.assertEqual(result.returncode, 0,
                                 f"Import crashed with LOG_LEVEL={level!r}:\n{result.stderr}")

    def test_invalid_levels_import_does_not_crash(self) -> None:
        """Invalid LOG_LEVEL values must not crash the import."""
        for level in ["DBUG", "TRACE", "VERBOSE", "INFOO", "WARINING"]:
            with self.subTest(level=level):
                result = self._import_logging_init(level)
                self.assertEqual(result.returncode, 0,
                                 f"Import crashed with LOG_LEVEL={level!r}:\n{result.stderr}")

    def test_case_insensitive_import(self) -> None:
        for level in ["Warning", "debug", "error", "fatal", "Warn"]:
            with self.subTest(level=level):
                result = self._import_logging_init(level)
                self.assertEqual(result.returncode, 0,
                                 f"Import crashed with LOG_LEVEL={level!r}:\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()
