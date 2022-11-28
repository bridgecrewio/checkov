from pathlib import Path

from checkov.argo_workflows.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.images.image_referencer import Image
from checkov.runner_filter import RunnerFilter
from checkov.argo_workflows.checks.registry import registry

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_registry_has_type():
    assert registry.report_type == CheckType.ARGO_WORKFLOWS


def test_runner_honors_enforcement_rules():
    # given
    test_file = EXAMPLES_DIR / "hello_world.yaml"

    # when
    filter = RunnerFilter(framework=['argo_workflows'], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.ARGO_WORKFLOWS: Severities[BcSeverities.OFF]}
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=filter)

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_passing_check():
    # given
    test_file = EXAMPLES_DIR / "hello_world.yaml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_ARGO_2"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 1
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_failing_check():
    # given
    test_file = EXAMPLES_DIR / "hello_world.yaml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV_ARGO_1"]))

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0


def test_runner_ignore_argo_cd():
    # given
    test_file = EXAMPLES_DIR / "argo_cd_application.yaml"

    # when
    report = Runner().run(root_folder="", files=[str(test_file)], runner_filter=RunnerFilter())

    # then
    summary = report.get_summary()

    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
    assert summary["resource_count"] == 0


def test_get_image():
    # given
    test_file = EXAMPLES_DIR / "scripts_python.yaml"

    # when
    images = Runner().get_images(str(test_file))

    # then
    assert images == {
        Image(
            file_path=str(test_file),
            name="alpine:latest",
            start_line=33,
            end_line=36,
        ),
        Image(
            file_path=str(test_file),
            name="python:alpine3.6",
            start_line=22,
            end_line=28,
        ),
    }

