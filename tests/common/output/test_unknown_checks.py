"""
Tests that UNKNOWN check results are stored and exposed in the report.
Run from repo root with: python -m pytest tests/common/output/test_unknown_checks.py -v
Or: python -m unittest tests.common.output.test_unknown_checks -v
"""
from __future__ import annotations

import unittest

from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report, merge_reports
from checkov.common.output.record import Record


def _make_record(result: CheckResult, check_id: str = "CKV_TEST_1", resource: str = "test.resource") -> Record:
    return Record(
        check_id=check_id,
        check_name="Test check",
        check_result={"result": result},
        code_block=[],
        file_path="test.tf",
        file_line_range=[1, 2],
        resource=resource,
        evaluations=None,
        check_class="test",
        file_abs_path="/test.tf",
    )


class TestUnknownChecksInReport(unittest.TestCase):
    """Verify UNKNOWN results are added to the report and appear in summary/output."""

    def test_add_record_unknown_appends_to_unknown_checks(self) -> None:
        report = Report("terraform")
        rec = _make_record(CheckResult.UNKNOWN)
        report.add_record(rec)
        self.assertEqual(len(report.unknown_checks), 1)
        self.assertIs(report.unknown_checks[0], rec)

    def test_unknown_not_added_to_passed_failed_or_skipped(self) -> None:
        report = Report("terraform")
        report.add_record(_make_record(CheckResult.UNKNOWN))
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.unknown_checks), 1)

    def test_get_summary_includes_unknown_count(self) -> None:
        report = Report("terraform")
        report.add_record(_make_record(CheckResult.UNKNOWN))
        report.add_record(_make_record(CheckResult.UNKNOWN, check_id="CKV_TEST_2", resource="other.resource"))
        summary = report.get_summary()
        self.assertIn("unknown", summary)
        self.assertEqual(summary["unknown"], 2)

    def test_get_all_records_includes_unknown_checks(self) -> None:
        report = Report("terraform")
        report.add_record(_make_record(CheckResult.PASSED))
        report.add_record(_make_record(CheckResult.UNKNOWN))
        all_records = report.get_all_records()
        self.assertEqual(len(all_records), 2)
        results = {r.check_result["result"] for r in all_records}
        self.assertEqual(results, {CheckResult.PASSED, CheckResult.UNKNOWN})

    def test_get_dict_includes_unknown_checks(self) -> None:
        report = Report("terraform")
        report.add_record(_make_record(CheckResult.UNKNOWN))
        d = report.get_dict()
        self.assertIn("results", d)
        self.assertIn("unknown_checks", d["results"])
        self.assertEqual(len(d["results"]["unknown_checks"]), 1)
        self.assertIn("unknown", d["summary"])
        self.assertEqual(d["summary"]["unknown"], 1)

    def test_from_reduced_json_without_unknown_checks_key(self) -> None:
        """Backward compatibility: JSON without unknown_checks still loads."""
        json_report = {
            "checks": {
                "passed_checks": [],
                "failed_checks": [],
                "skipped_checks": [],
            },
            "image_cached_results": [],
        }
        report = Report.from_reduced_json(json_report, "terraform")
        self.assertEqual(len(report.unknown_checks), 0)
        self.assertIn("unknown", report.get_summary())
        self.assertEqual(report.get_summary()["unknown"], 0)

    def test_from_reduced_json_with_unknown_checks(self) -> None:
        """JSON with unknown_checks loads them."""
        json_report = {
            "checks": {
                "passed_checks": [],
                "failed_checks": [],
                "skipped_checks": [],
                "unknown_checks": [
                    {
                        "check_id": "CKV_UNKNOWN_1",
                        "bc_check_id": "BC_UNKNOWN_1",
                        "check_name": "Unknown check",
                        "check_result": {"result": "UNKNOWN"},
                        "code_block": [],
                        "file_path": "f.tf",
                        "file_line_range": [1, 2],
                        "resource": "res",
                        "evaluations": None,
                        "check_class": "c",
                        "file_abs_path": "/f.tf",
                    }
                ],
            },
            "image_cached_results": [],
        }
        report = Report.from_reduced_json(json_report, "terraform")
        self.assertEqual(len(report.unknown_checks), 1)
        self.assertEqual(report.unknown_checks[0].check_id, "CKV_UNKNOWN_1")
        self.assertEqual(report.get_summary()["unknown"], 1)

    def test_merge_reports_includes_unknown_checks(self) -> None:
        base = Report("terraform")
        base.add_record(_make_record(CheckResult.UNKNOWN, resource="r1"))
        other = Report("terraform")
        other.add_record(_make_record(CheckResult.UNKNOWN, resource="r2"))
        merge_reports(base, other)
        self.assertEqual(len(base.unknown_checks), 2)

    def test_record_to_string_unknown_has_status(self) -> None:
        rec = _make_record(CheckResult.UNKNOWN)
        s = rec.to_string()
        self.assertIn("UNKNOWN", s)
        self.assertIn("test.resource", s)


if __name__ == "__main__":
    unittest.main()
