import json
import os
from typing import List, Dict, Any
import yaml


current_dir = os.path.dirname(os.path.realpath(__file__))


def load_failed_checks_from_file(lang: str) -> Dict[str, List[Dict[str, Any]]]:
    report_path = os.path.join(current_dir, '..', 'checkov_report_cdk.json')
    with open(report_path) as f:
        data = f.read()
        reports = json.loads(data)
        for report in reports:
            if report.get('check_type') == f'cdk_{lang}':
                assert report is not None
                results = report.get("results", {})
                failed_checks = results.get("failed_checks")
                skipped_checks = results.get("skipped_checks")
                results = {}
                for check in failed_checks:
                    check_id = check['check_id']
                    if not results.get(check_id):
                        results[check_id] = []
                    results[check_id].append(check)
                for check in skipped_checks:
                    check_id = check['check_id']
                    if not results.get(check_id):
                        results[check_id] = []
                    results[check_id].append(check)
                return results
    return {}


def is_policy_with_correct_check_id(check_id: str, language: str, policy_name: str) -> bool:
    path = os.path.join(current_dir, '..', 'checkov', 'cdk', 'checks', language, policy_name + ".yaml")
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    if 'metadata' in data and 'id' in data['metadata'] and data['metadata']['id'] == check_id:
        return True
    return False


def run_check(check_results: Dict[str, List[Dict[str, Any]]], check_id: str, policy_name: str, language: str) -> None:
    assert is_policy_with_correct_check_id(check_id, language, policy_name)
    results_for_check_id = check_results.get(check_id)
    assert results_for_check_id


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
