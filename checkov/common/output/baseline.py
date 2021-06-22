from collections import defaultdict
from typing import Dict, List, DefaultDict

from checkov.common.output.report import Report


class Baseline:
    failed_checks: DefaultDict[str, List[Dict[str, List[str]]]] = defaultdict(list)

    def add_findings_from_report(self, report: Report) -> None:
        for check in report.failed_checks:
            try:
                existing = next(x for x in self.failed_checks[check.file_path] if x['resource'] == check.resource)
            except StopIteration:
                existing = {"resource": check.resource, "check_ids": []}
                self.failed_checks[check.file_path].append(existing)
            existing['check_ids'].append(check.check_id)
            existing['check_ids'].sort()  # Sort the check IDs to be nicer to the eye

    def to_dict(self) -> dict:
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
        for file, findings in self.failed_checks.items():
            formatted_findings = []
            for finding in findings:
                formatted_findings.append({"resource": finding['resource'], "check_ids": finding["check_ids"]})
            failed_checks_list.append({"file": file, "findings": formatted_findings})

        resp = {
            "failed_checks": failed_checks_list
        }
        return resp

    # TODO: implement read from JSON
    # @staticmethod
    # def from_json(o: dict) -> "Baseline":
    #     baseline = Baseline()
    #     baseline.failed_checks = ...
    #     return baseline
