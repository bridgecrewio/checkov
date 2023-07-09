from pathlib import Path

from checkov.bicep.runner import Runner
from checkov.arm.checks.resource.AzureFirewallDenyThreatIntelMode import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_AzureFirewallDenyThreatIntelMode"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        "Microsoft.Network/azureFirewalls.pass",
    }
    failing_resources = {
        "Microsoft.Network/azureFirewalls.fail",
        "Microsoft.Network/azureFirewalls.fail2",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == len(passing_resources)
    assert summary["failed"] == len(failing_resources)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passing_resources == passed_check_resources
    assert failing_resources == failed_check_resources
