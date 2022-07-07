from pathlib import Path

import pytest

from checkov.bicep.runner import Runner
from checkov.arm.runner import Runner as ArmRunner
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"


@pytest.fixture(autouse=True)
def load_arm_checks():
    # just initialize to add the ARM checks to the Bicep registry
    ArmRunner()


def test_arm_checks_laoded():
    # when
    resource_registry = Runner.block_type_registries["resources"]

    # then
    assert len(resource_registry.checks) > 30


def test_runner_passing_check():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_3"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_failing_check():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_9"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_skipping_check():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_35"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 1
    assert summary["parsing_errors"] == 0


def test_runner_parsing_errors():
    # given
    test_file = EXAMPLES_DIR / "malformed.bicep"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_35"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 1


def test_runner_ignore_existing_resource():
    # given
    test_file = EXAMPLES_DIR / "existing.bicep"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_35"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
    assert summary["resource_count"] == 2  # 1 should be unknown

    assert report.failed_checks[0].resource == "Microsoft.Storage/storageAccounts.storageAccount"


def test_runner_extra_resources():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_AZURE_3"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1

    assert len(report.extra_resources) == 7
    extra_resource = next(
        resource for resource in report.extra_resources if resource.resource == "Microsoft.Compute/virtualMachines.vm"
    )
    assert extra_resource.file_abs_path == str(test_file)
    assert extra_resource.file_path.endswith("playground.bicep")

