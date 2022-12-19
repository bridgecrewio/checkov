import json
import os
from pathlib import Path

from pytest_mock import MockerFixture

from checkov.azure_devops.registry import registry
from checkov.azure_devops.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_registry_has_type():
    assert registry.report_type == CheckType.AZURE_DEVOPS_CONFIGURATION


def test_runner_honors_enforcement_rules():
    # given
    filter = RunnerFilter(framework=["azure_devops_configuration"], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.AZURE_DEVOPS_CONFIGURATION: Severities[BcSeverities.OFF]}

    # when
    report = Runner().run(runner_filter=filter)

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_passing_check(mocker: MockerFixture, tmp_path: Path):
    # given
    test_file = EXAMPLES_DIR / "minimum_number_of_reviewers.json"

    mocker.patch("checkov.azure_devops.dal.AzureDevOps._request", return_value=json.loads(test_file.read_text()))
    mocker.patch("checkov.azure_devops.dal.Path.cwd", return_value=tmp_path)

    mocker.patch.dict(
        os.environ,
        {
            "BUILD_REPOSITORY_ID": "12345678-abcd-1234-abcd-1234567890",
            "SYSTEM_PULLREQUEST_TARGETBRANCH": "refs/heads/main",
        },
    )

    # when
    report = Runner().run(runner_filter=RunnerFilter(checks=["CKV_AZUREDEVOPS_2"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_failing_check(mocker: MockerFixture, tmp_path: Path):
    # given
    test_file = EXAMPLES_DIR / "minimum_number_of_reviewers.json"

    mocker.patch("checkov.azure_devops.dal.AzureDevOps._request", return_value=json.loads(test_file.read_text()))
    mocker.patch("checkov.azure_devops.dal.Path.cwd", return_value=tmp_path)

    mocker.patch.dict(
        os.environ,
        {
            "BUILD_REPOSITORY_ID": "12345678-abcd-1234-abcd-1234567890",
            "SYSTEM_PULLREQUEST_TARGETBRANCH": "refs/heads/main",
        },
    )

    # when
    report = Runner().run(runner_filter=RunnerFilter(checks=["CKV_AZUREDEVOPS_1"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
