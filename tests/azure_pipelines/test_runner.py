from pathlib import Path

from checkov.azure_pipelines.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.azure_pipelines.checks.registry import registry

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_registry_has_type():
    assert registry.report_type == CheckType.AZURE_PIPELINES


def test_runner_honors_enforcement_rules():
    # given
    test_file = EXAMPLES_DIR / "azure-pipelines.yml"

    # when
    filter = RunnerFilter(framework=["azure_pipelines"], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.AZURE_PIPELINES: Severities[BcSeverities.OFF]}
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=filter)

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_passing_check():
    # given
    test_file = EXAMPLES_DIR / "azure-pipelines.yml"

    # when
    report = Runner().run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZUREPIPELINES_1"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_failing_check():
    # given
    test_file = EXAMPLES_DIR / "azure-pipelines.yml"

    # when
    report = Runner().run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZUREPIPELINES_2"])
    )

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
