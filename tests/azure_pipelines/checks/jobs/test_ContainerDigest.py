from pathlib import Path

from checkov.azure_pipelines.runner import Runner
from checkov.azure_pipelines.checks.job.ContainerDigest import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_ContainerDigest"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        f"stages[0](ExampleDisplayName).jobs[1](PassDigestDisplayName)",
    }

    failing_resources = {
        f"jobs[0](FailTag)",
        f"stages[0](ExampleDisplayName).jobs[0](FailNoTag)",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
