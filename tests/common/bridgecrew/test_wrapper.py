
def test_reduce_scan_reports_secrets(report):
    from checkov.common.bridgecrew.wrapper import reduce_scan_reports
    from checkov.common.typing import _ReducedScanReportCheck, _ReducedScanReport
    from checkov.common.bridgecrew.check_type import CheckType

    reduced_report: _ReducedScanReport = reduce_scan_reports([report])[CheckType.SECRETS]

    checks: _ReducedScanReportCheck = reduced_report["checks"]
    all_checks = checks["passed_checks"] + checks["failed_checks"] + checks["skipped_checks"]

    assert all('validation_status' in check.keys() for check in all_checks)


def test_reduce_scan_reports(report):
    from checkov.common.bridgecrew.wrapper import reduce_scan_reports
    from checkov.common.typing import _ReducedScanReportCheck, _ReducedScanReport
    from checkov.common.bridgecrew.check_type import CheckType

    report.check_type = CheckType.GITHUB_ACTIONS
    reduced_report: _ReducedScanReport = reduce_scan_reports([report])[CheckType.GITHUB_ACTIONS]

    checks: _ReducedScanReportCheck = reduced_report["checks"]
    all_checks = checks["passed_checks"] + checks["failed_checks"] + checks["skipped_checks"]

    reduced_keys = ('check_id', 'check_result', 'resource', 'file_path', 'file_line_range')

    assert all(reduced_key in check.keys() for check in all_checks for reduced_key in reduced_keys)
    assert all('validation_status' not in check.keys() for check in all_checks)
