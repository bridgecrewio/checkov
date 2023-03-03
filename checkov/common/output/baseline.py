from __future__ import annotations

import json
from collections import defaultdict
from operator import itemgetter

from checkov.common.models.enums import CheckResult
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaselineFinding, _BaselineFailedChecks


class Baseline:
    def __init__(self, output_skipped: bool = False) -> None:
        self.path = ""
        self.path_failed_checks_map: dict[str, list[_BaselineFinding]] = defaultdict(list)
        self.failed_checks: list[_BaselineFailedChecks] = []
        self.output_skipped = output_skipped

    def add_findings_from_report(self, report: Report) -> None:
        for check in report.failed_checks:
            try:
                existing = next(
                    x for x in self.path_failed_checks_map[check.file_path] if x["resource"] == check.resource
                )
            except StopIteration:
                existing = {"resource": check.resource, "check_ids": []}
                self.path_failed_checks_map[check.file_path].append(existing)
            existing["check_ids"].append(check.check_id)
            existing["check_ids"].sort()  # Sort the check IDs to be nicer to the eye

    def to_dict(self) -> dict[str, Any]:
        """
        The output of this class needs to be very explicit, hence the following structure of the dict:
        {
            "failed_checks": [
                {
                    "file": "path/to/file",
                    "findings: [
                        {
                            "resource": "aws_s3_bucket.this",
                            "check_ids": [
                                "CKV_AWS_1",
                                "CKV_AWS_2",
                                "CKV_AWS_3"
                            ]
                        }
                    ]
                }
            ]
        }
        """
        failed_checks_list = []
        for file, findings in self.path_failed_checks_map.items():
            formatted_findings = []
            for finding in findings:
                formatted_findings.append({"resource": finding["resource"], "check_ids": finding["check_ids"]})
            sorted_findings = sorted(formatted_findings, key=itemgetter("resource"))
            failed_checks_list.append({"file": file, "findings": sorted_findings})

        resp = {"failed_checks": sorted(failed_checks_list, key=itemgetter("file"))}
        return resp

    def compare_and_reduce_reports(self, scan_reports: list[Report]) -> None:
        for scan_report in scan_reports:
            scan_report.passed_checks = [
                check for check in scan_report.passed_checks if self._is_check_in_baseline(check)
            ]
            scan_report.skipped_checks = [
                check for check in scan_report.skipped_checks if self._is_check_in_baseline(check)
            ]
            if self.output_skipped:
                for check in scan_report.failed_checks:
                    if self._is_check_in_baseline(check):
                        check.check_result["suppress_comment"] = "baseline-skipped"
                        check.check_result["result"] = CheckResult.SKIPPED
                        scan_report.skipped_checks.append(check)
            scan_report.failed_checks = [
                check for check in scan_report.failed_checks if not self._is_check_in_baseline(check)
            ]

    def _is_check_in_baseline(self, check: Record) -> bool:
        failed_check_id = check.check_id
        failed_check_resource = check.resource
        for baseline_failed_check in self.failed_checks:
            for finding in baseline_failed_check["findings"]:
                if finding["resource"] == failed_check_resource and failed_check_id in finding["check_ids"]:
                    return True
        return False

    def from_json(self, file_path: str) -> None:
        self.path = file_path
        with open(file_path, "r") as f:
            baseline_raw = json.load(f)
            self.failed_checks = baseline_raw.get("failed_checks", {})
