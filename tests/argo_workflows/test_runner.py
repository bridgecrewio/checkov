from pathlib import Path

from checkov.argo_workflows.runner import Runner
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"


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
