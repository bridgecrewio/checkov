from pathlib import Path

from checkov.bicep.runner import Runner
from checkov.arm.checks.resource.FrontdoorUseWAFMode import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_FrontdoorUseWAFMode"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        "Microsoft.Network/FrontDoorWebApplicationFirewallPolicies.pass",
    }
    failing_resources = {
        "Microsoft.Network/FrontDoorWebApplicationFirewallPolicies.fail",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
