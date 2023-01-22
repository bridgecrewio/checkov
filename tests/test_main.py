from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import Literal

from checkov import main
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.main import DEFAULT_RUNNERS, Checkov
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    import argparse
    from checkov.common.output.baseline import Baseline
    from checkov.common.output.report import Report


class CustomRunnerRegistry(RunnerRegistry):
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
        # result doesn't matter, just don't want it to print to console
        return 0


def test_run_with_outer_registry_and_framework_flag():
    # given
    custom_banner = "custom banner"
    resource_dir = Path(__file__).parent / "common/runner_registry/example_multi_iac"
    argv = ["-d", str(resource_dir), "--framework", "terraform"]

    # when
    main.outer_registry = CustomRunnerRegistry(custom_banner, RunnerFilter(), *DEFAULT_RUNNERS)
    ckv = Checkov()
    ckv.parse_config(argv=argv)
    ckv.run(banner=custom_banner)

    # then
    assert len(main.outer_registry.runners) == 1
    assert main.outer_registry.runners[0].check_type == "terraform"

    # cleanup
    main.outer_registry = None


def test_run():
    # given
    custom_banner = "custom banner"
    resource_dir = Path(__file__).parent / "common/runner_registry/example_multi_iac"
    argv = ["-d", str(resource_dir), "--framework", "terraform", "kubernetes"]

    # when
    ckv = Checkov()
    ckv.parse_config(argv=argv)
    ckv.run(banner=custom_banner)

    # then
    # check run_metadata has all fields set
    assert ckv.run_metadata["checkov_version"] and isinstance(ckv.run_metadata["checkov_version"], str)
    assert ckv.run_metadata["python_executable"] and isinstance(ckv.run_metadata["python_executable"], str)
    assert ckv.run_metadata["python_version"] and isinstance(ckv.run_metadata["python_version"], str)
    assert ckv.run_metadata["checkov_executable"] and isinstance(ckv.run_metadata["checkov_executable"], str)
    assert ckv.run_metadata["args"] and isinstance(ckv.run_metadata["args"], list)

    # check all runners were initialized, but only 2 were actually run
    assert len(ckv.runners) == 27

    assert len(ckv.scan_reports) == 2
    assert {report.check_type for report in ckv.scan_reports} == {"kubernetes", "terraform"}
