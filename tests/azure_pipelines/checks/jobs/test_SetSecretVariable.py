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
        f"{test_files_dir}/azure-pipelines.yml.stages[].jobs[].steps[].stages[].jobs[].steps[].CKV_AZUREPIPELINES_3[17:19]",
        f"{test_files_dir}/azure-pipelines.yml.stages[].jobs[].steps[].stages[].jobs[].steps[].CKV_AZUREPIPELINES_3[19:21]",
        f"{test_files_dir}/azure-pipelines.yml.jobs[].steps[].jobs[].steps[].CKV_AZUREPIPELINES_3[49:51]",
        f"{test_files_dir}/azure-pipelines.yml.jobs[].steps[].jobs[].steps[].CKV_AZUREPIPELINES_3[51:53]",
    }

    failing_resources = {
        f"{test_files_dir}/azure-pipelines.yml.jobs[].steps[].jobs[].steps[].CKV_AZUREPIPELINES_3[38:41]",
        f"{test_files_dir}/azure-pipelines.yml.jobs[].steps[].jobs[].steps[].CKV_AZUREPIPELINES_3[41:45]",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
