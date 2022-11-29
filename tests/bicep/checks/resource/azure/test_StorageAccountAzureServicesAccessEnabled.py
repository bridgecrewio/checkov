from pathlib import Path

from checkov.bicep.runner import Runner
from checkov.bicep.checks.resource.azure.StorageAccountAzureServicesAccessEnabled import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_StorageAccountAzureServicesAccessEnabled"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        "Microsoft.Storage/storageAccounts.allowAll",
        "Microsoft.Storage/storageAccounts.default",
        "Microsoft.Storage/storageAccounts.denyAndBypass",
    }

    failing_resources = {
        "Microsoft.Storage/storageAccounts.deny",
        "Microsoft.Storage/storageAccounts.denyAndBypassNone",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0
    assert summary["resource_count"] == len(passing_resources) + len(failing_resources) + 1  # unknown

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
