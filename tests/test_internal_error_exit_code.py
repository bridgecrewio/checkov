from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch, MagicMock

from typing_extensions import Literal

from checkov import main
from checkov.common.models.enums import ErrorStatus
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.main import Checkov
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    import argparse
    from checkov.common.output.baseline import Baseline


RESOURCE_DIR = str(Path(__file__).parent / "common/runner_registry/example_multi_iac")


class NoOutputRunnerRegistry(RunnerRegistry):
    """A runner registry that suppresses output for testing."""

    def __init__(self, banner: str, runner_filter: RunnerFilter, *runners: BaseRunner) -> None:
        super().__init__(banner, runner_filter, *runners)

    def print_reports(
        self,
        scan_reports: list[Report],
        config: argparse.Namespace,
        url: str | None = None,
        created_baseline_path: str | None = None,
        baseline: Baseline | None = None,
    ) -> Literal[0, 1]:
        return 0


def _make_checkov(extra_argv: list[str] | None = None) -> Checkov:
    argv = ["-d", RESOURCE_DIR, "--framework", "terraform"]
    if extra_argv:
        argv.extend(extra_argv)
    ckv = Checkov(argv=argv)
    return ckv


def test_normal_run_returns_zero_or_one():
    """A normal run without internal errors returns 0 (pass) or 1 (failed checks)."""
    ckv = _make_checkov()
    # suppress output
    with patch.dict(os.environ, {"CHECKOV_NO_OUTPUT": "True"}):
        exit_code = ckv.run()
    assert exit_code in (0, 1), f"Expected 0 or 1, got {exit_code}"
    assert not ckv._internal_error_occurred


def test_exit_code_2_on_report_error():
    """When a report has an error status, the exit code should be 2."""
    ckv = _make_checkov()

    original_run = RunnerRegistry.run

    def patched_run(self, *args, **kwargs):
        results = original_run(self, *args, **kwargs)
        # Simulate an internal error in one of the reports
        if results:
            results[0].error_status = ErrorStatus.ERROR
        return results

    with patch.dict(os.environ, {"CHECKOV_NO_OUTPUT": "True"}):
        with patch.object(RunnerRegistry, "run", patched_run):
            exit_code = ckv.run()

    assert exit_code == 2, f"Expected exit code 2 for internal error, got {exit_code}"
    assert ckv._internal_error_occurred


def test_exit_code_0_on_report_error_with_no_fail_on_crash():
    """When --no-fail-on-crash is set, internal errors return exit code 0."""
    ckv = _make_checkov(extra_argv=["--no-fail-on-crash"])

    original_run = RunnerRegistry.run

    def patched_run(self, *args, **kwargs):
        results = original_run(self, *args, **kwargs)
        if results:
            results[0].error_status = ErrorStatus.ERROR
        return results

    with patch.dict(os.environ, {"CHECKOV_NO_OUTPUT": "True"}):
        with patch.object(RunnerRegistry, "run", patched_run):
            exit_code = ckv.run()

    assert exit_code == 0, f"Expected exit code 0 with --no-fail-on-crash, got {exit_code}"
    assert ckv._internal_error_occurred


def test_exit_code_2_on_unhandled_exception():
    """When an unhandled exception occurs during the run, exit code should be 2."""
    ckv = _make_checkov()

    with patch.dict(os.environ, {"CHECKOV_NO_OUTPUT": "True"}):
        with patch.object(RunnerRegistry, "run", side_effect=RuntimeError("simulated internal error")):
            exit_code = ckv.run()

    assert exit_code == 2, f"Expected exit code 2 for unhandled exception, got {exit_code}"
    assert ckv._internal_error_occurred


def test_exit_code_0_on_unhandled_exception_with_no_fail_on_crash():
    """When an unhandled exception occurs with --no-fail-on-crash, exit code should be 0."""
    ckv = _make_checkov(extra_argv=["--no-fail-on-crash"])

    with patch.dict(os.environ, {"CHECKOV_NO_OUTPUT": "True"}):
        with patch.object(RunnerRegistry, "run", side_effect=RuntimeError("simulated internal error")):
            exit_code = ckv.run()

    assert exit_code == 0, f"Expected exit code 0 with --no-fail-on-crash, got {exit_code}"
    assert ckv._internal_error_occurred


def test_internal_error_flag_from_platform_integration():
    """When bc_integration.internal_error_occurred is set, exit code should be 2."""
    ckv = _make_checkov()

    from checkov.common.bridgecrew.platform_integration import bc_integration

    # Simulate a platform integration internal error
    original_value = bc_integration.internal_error_occurred
    try:
        bc_integration.internal_error_occurred = True
        with patch.dict(os.environ, {"CHECKOV_NO_OUTPUT": "True"}):
            exit_code = ckv.run()
        assert exit_code == 2, f"Expected exit code 2 for platform integration error, got {exit_code}"
        assert ckv._internal_error_occurred
    finally:
        bc_integration.internal_error_occurred = original_value


def test_get_exit_code_for_internal_error():
    """Test the _get_exit_code_for_internal_error helper method."""
    ckv = _make_checkov()
    assert ckv._get_exit_code_for_internal_error() == 2

    ckv_no_fail = _make_checkov(extra_argv=["--no-fail-on-crash"])
    assert ckv_no_fail._get_exit_code_for_internal_error() == 0
