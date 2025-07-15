import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Union
from checkov.common.output.report import Report
import os
import hashlib


class InTotoOutput:
    def __init__(self, repo_id: Union[str, None], reports: List[Report]):
        self.repo_id = f"{repo_id}/" if repo_id else ""
        self.reports = reports

    @staticmethod
    def calculate_sha256(file_path: str) -> str:
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    def generate_output(self) -> Dict[str, Any]:
        scan_start_time = datetime.now(timezone.utc).isoformat()

        in_toto_data: Dict[str, Any] = {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": [
                {
                    "name": "",
                    "digest": {
                        "sha256": ""
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
                file_path = check.file_path
                sha256_hash = self.calculate_sha256(file_path)

                in_toto_data["predicate"]["invocation"]["uri"] = ""
                in_toto_data["predicate"]["invocation"]["event_id"] = "1071875574"
                in_toto_data["predicate"]["invocation"]["builder.id"] = ""
                in_toto_data["predicate"]["scanner"]["uri"] = ""
                in_toto_data["predicate"]["scanner"]["version"] = "0.19.2"
                in_toto_data["predicate"]["scanner"]["db"]["uri"] = "pkg:github/aquasecurity/trivy-db/commit/4c76bb580b2736d67751410fa4ab66d2b6b9b27d"
                in_toto_data["predicate"]["scanner"]["db"]["version"] = "v1-2021080612"
                in_toto_data["predicate"]["scanner"]["db"]["lastUpdate"] = "2021-08-06T17:45:50.52Z"
                in_toto_data["subject"][0]["name"] = os.path.basename(file_path)
                in_toto_data["subject"][0]["digest"]["sha256"] = sha256_hash

                result_data: Dict[str, Any] = {
                    "id": check.check_id,
                    "severity": [
                        {
                            "method": "vendor",
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
            json.dump(in_toto_data, f, indent=4)
