import json
import os

current_dir = os.path.dirname(os.path.realpath(__file__))


def run_check(lang: str, check_name: str) -> None:
    report_path = os.path.join(current_dir, '..', f'checkov_report_cdk_{lang}_{check_name}.json')
    validate_report(os.path.abspath(report_path))


def validate_report(report_path: str) -> None:
    with open(report_path) as f:
        data = f.read()
        report = json.loads(data)
        assert report is not None
        results = report.get("results")
        assert results is not None
        passed_checks = results.get("passed_checks")
        failed_checks = results.get("failed_checks")
        assert not passed_checks
        assert failed_checks is not None
        assert isinstance(failed_checks, list)
        assert len(failed_checks) > 0
        summary = report.get("summary")
        assert summary.get("passed") == 0
        assert summary.get("failed") > 0
