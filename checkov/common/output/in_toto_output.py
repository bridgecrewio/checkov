import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Union
from checkov.common.output.report import Report
import os


class InTotoOutput:
    def __init__(self, repo_id: Union[str, None], reports: List[Report]):
        self.repo_id = f"{repo_id}/" if repo_id else ""
        self.reports = reports

    def generate_output(self) -> Dict[str, Any]:
        scan_start_time = datetime.now(timezone.utc).isoformat()

        in_toto_data = {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": [
                {
                    "name": "",
                    "digest": {
                        "sha256": "fe4fe40ac7250263c5dbe1cf3138912f3f416140aa248637a60d65fe22c47da4"
                    }
                }
            ],
            "predicateType": "https://in-toto.io/attestation/vulns/v0.1",
            "predicate": {
                "invocation": {
                    "parameters": [],
                    "uri": "",
                    "event_id": "",
                    "builder.id": ""
                },
                "scanner": {
                    "uri": "",
                    "version": "",
                    "db": {
                        "uri": "",
                        "version": "",
                        "lastUpdate": ""
                    },
                    "result": [
                        {
                            "id": "",
                            "severity": [
                                {
                                    "method": "nvd",
                                    "score": ""
                                },
                                {
                                    "method": "cvss_score",
                                    "score": ""
                                }
                            ],
                            "annotations": [],
                            "scanStartedOn": ""
                        }
                    ]
                },
                "metadata": {
                    "scanStartedOn": scan_start_time,
                    "scanFinishedOn": ""
                }
            }
        }

        for report in self.reports:
            for check in report.failed_checks:
                in_toto_data["predicate"]["invocation"]["uri"] = "https://github.com/developer-guy/alpine/actions/runs/1071875574"
                in_toto_data["predicate"]["invocation"]["event_id"] = "1071875574"
                in_toto_data["predicate"]["invocation"]["builder.id"] = "GitHub Actions"
                in_toto_data["predicate"]["scanner"]["uri"] = "pkg:github/aquasecurity/trivy@244fd47e07d1004f0aed9"
                in_toto_data["predicate"]["scanner"]["version"] = "0.19.2"
                in_toto_data["predicate"]["scanner"]["db"]["uri"] = "pkg:github/aquasecurity/trivy-db/commit/4c76bb580b2736d67751410fa4ab66d2b6b9b27d"
                in_toto_data["predicate"]["scanner"]["db"]["version"] = "v1-2021080612"
                in_toto_data["predicate"]["scanner"]["db"]["lastUpdate"] = "2021-08-06T17:45:50.52Z"
                in_toto_data["subject"][0]["name"] = os.path.basename(check.file_path)

                result_data = {
                    "id": check.check_id,
                    "severity": [
                        {
                            "method": "nvd",
                            "score": check.severity
                        }
                    ],
                    "annotations": [{"key": "description", "value": check.check_name}],
                    "scanStartedOn": scan_start_time
                }

                in_toto_data["predicate"]["scanner"]["result"][0] = result_data

        scan_finish_time = datetime.now(timezone.utc).isoformat()
        in_toto_data["predicate"]["metadata"]["scanFinishedOn"] = scan_finish_time

        return in_toto_data

    @staticmethod
    def write_output(output_path: str, in_toto_data: Dict[str, Any]) -> None:
        with open(output_path, "w") as f:
            json.dump(in_toto_data, f, indent=4),
