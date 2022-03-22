from pathlib import Path

from checkov.bicep.runner import Runner
from checkov.bicep.checks.resource.azure.SQLServerAuditingEnabled import check
from checkov.runner_filter import RunnerFilter


def test_examples():
    # given
    test_files_dir = Path(__file__).parent / "example_SQLServerAuditingEnabled"

    # when
    report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

    # then
    summary = report.get_summary()

    passing_resources = {
        "Microsoft.Sql/servers/auditingSettings.serverEnabled",
        "Microsoft.Sql/servers/databases/auditingSettings.dbEnabled",
        "Microsoft.Sql/servers/auditingSettings.nestedAudit",
    }

    failing_resources = {
        "Microsoft.Sql/servers/auditingSettings.serverDefault",
        "Microsoft.Sql/servers/auditingSettings.serverDisabled",
        "Microsoft.Sql/servers/databases/auditingSettings.dbDefault",
        "Microsoft.Sql/servers/databases/auditingSettings.dbDisabled",
    }

    passed_check_resources = {c.resource for c in report.passed_checks}
    failed_check_resources = {c.resource for c in report.failed_checks}

    assert summary["passed"] == 3
    assert summary["failed"] == 4
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_check_resources == passing_resources
    assert failed_check_resources == failing_resources
