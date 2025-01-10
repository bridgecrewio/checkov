from __future__ import annotations

import unittest
from typing import Union

from checkov.common.output.report import Report


def checks_report_assertions(test_case: unittest.TestCase, report: Report,
                             expected_passing_resources: set[str],
                             expected_failing_resources: Union[set[str], dict[str, list[str]]],
                             expected_skipped_resources: set[str] = None) -> None:
    """
    validates:
    1. summary field includes correct count of passing / failing / skipped resources
    2. the resource themselves match the expected resources
    3. for failing resources, there's an option to send expected as dict, in which case both the resource and the evaluated keys of that check will be validated
    """
    if expected_skipped_resources is None:
        expected_skipped_resources = set()

    summary = report.get_summary()

    passed_check_resources = {c.resource for c in report.passed_checks}
    skipped_check_resources = {c.resource for c in report.skipped_checks}

    if isinstance(expected_failing_resources, dict):
        failed_check_resources = {c.resource: c.check_result.get("evaluated_keys") for c in report.failed_checks}
    else:
        failed_check_resources = {c.resource for c in report.failed_checks}

    test_case.assertEqual(summary["passed"], len(expected_passing_resources))
    test_case.assertEqual(summary["failed"], len(expected_failing_resources))
    test_case.assertEqual(summary["skipped"], len(expected_skipped_resources))
    test_case.assertEqual(summary["parsing_errors"], 0)

    test_case.assertEqual(expected_passing_resources, passed_check_resources)
    test_case.assertEqual(expected_failing_resources, failed_check_resources)
    test_case.assertEqual(expected_skipped_resources, skipped_check_resources)