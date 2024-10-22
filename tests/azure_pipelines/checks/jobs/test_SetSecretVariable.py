from pathlib import Path

from checkov.azure_pipelines.runner import Runner
from checkov.azure_pipelines.checks.job.SetSecretVariable import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_SetSecretVariable"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        f"jobs[1](PassSetNormalVariable).steps[0]",
        f"jobs[1](PassSetNormalVariable).steps[1]",
        f"stages[0](Example).jobs[0](PassSetNoSecretVariable).steps[0]",
        f"stages[0](Example).jobs[0](PassSetNoSecretVariable).steps[1]",
    }

    failing_resources = {
        f"jobs[0](FailSetSecretVariable).steps[0](setSecretVariableStep)",
        f"jobs[0](FailSetSecretVariable).steps[1]",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
