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
        f"{test_files_dir}/azure-pipelines.yml.stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_2[22:31]",
    }

    failing_resources = {
        f"{test_files_dir}/azure-pipelines.yml.jobs.jobs.CKV_AZUREPIPELINES_2[32:40]",
        f"{test_files_dir}/azure-pipelines.yml.stages[].jobs[].stages[].jobs[].CKV_AZUREPIPELINES_2[14:22]",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
