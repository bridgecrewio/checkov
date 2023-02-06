from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from checkov.common.output.cyclonedx_consts import SCA_CHECKTYPES
from checkov.version import version

if TYPE_CHECKING:
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report

DEFAULT_SEVERITY_GITLAB_LEVEL = "Unknown"
SEVERITY_TO_GITLAB_LEVEL = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "none": "Info",
}


class GitLabSast:
    def __init__(self, reports: list[Report]):
        self.reports = reports

        self.sast_json = self.create_sast_json()

    def create_sast_json(self) -> dict[str, Any]:
        return {
            "schema": "https://gitlab.com/gitlab-org/security-products/security-report-schemas/-/raw/v15.0.4/dist/sast-report-format.json",
            "version": "15.0.4",
            "scan": self._create_scan(),
            "vulnerabilities": self._create_vulnerabilities(),
        }

    def _create_scan(self) -> dict[str, Any]:
        current_datetime = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        scanner = {
            "id": "checkov",
            "name": "Checkov",
            "url": "https://www.checkov.io/",
            "vendor": {
                "name": "Bridgecrew",
            },
            "version": version,
        }

        return {
            "start_time": current_datetime,  # needs to be done properly in a later stage
            "end_time": current_datetime,
            "analyzer": scanner,  # same for us
            "scanner": scanner,
            "status": "success",
            "type": "sast",
        }

    def _create_vulnerabilities(self) -> list[dict[str, Any]]:
        vulnerabilities = []

        for report in self.reports:
            if report.check_type in SCA_CHECKTYPES:
                for check in report.failed_checks:
                    vulnerability = None
                    if check.check_id.startswith("BC_LIC"):
                        vulnerability = self._create_license_vulnerability(record=check)
                    elif check.check_id.startswith(("BC_VUL", "CKV_CVE")):
                        vulnerability = self._create_cve_vulnerability(record=check)

                    if vulnerability:
                        vulnerabilities.append(vulnerability)
            else:
                for check in report.failed_checks:
                    vulnerabilities.append(self._create_iac_vulnerability(record=check))

        return vulnerabilities

    def _create_iac_vulnerability(self, record: Record) -> dict[str, Any]:
        severity = record.severity.name.lower() if record.severity else ""

        vulnerability: "dict[str, Any]" = {
            "id": str(uuid4()),
            "identifiers": [
                {
                    "name": record.check_id,
                    "type": "checkov",
                    "value": record.check_id,
                }
            ],
            "location": {
                "file": record.repo_file_path.lstrip("/"),
                "start_line": record.file_line_range[0],
                "end_line": record.file_line_range[1],
            },
            "name": record.check_name,
            "description": f"Further info can be found {record.guideline}",
            "severity": SEVERITY_TO_GITLAB_LEVEL.get(severity, DEFAULT_SEVERITY_GITLAB_LEVEL),
            "solution": f"Further info can be found {record.guideline}",
        }

        if record.guideline:
            # url can't be None
            vulnerability["identifiers"][0]["url"] = record.guideline
            vulnerability["links"] = [
                {
                    "url": record.guideline,
                }
            ]

        return vulnerability

    def _create_cve_vulnerability(self, record: Record) -> dict[str, Any] | None:
        details = record.vulnerability_details
        if not details:
            # this shouldn't happen
            return None

        severity = record.severity.name.lower() if record.severity else ""

        vulnerability: "dict[str, Any]" = {
            "id": str(uuid4()),
            "identifiers": [
                {
                    "name": record.short_description,
                    "type": "cve",
                    "value": details["id"],
                }
            ],
            "location": {
                "file": record.repo_file_path.lstrip("/"),
            },
            "name": record.short_description,
            "description": details.get("description"),
            "severity": SEVERITY_TO_GITLAB_LEVEL.get(severity, DEFAULT_SEVERITY_GITLAB_LEVEL),
            "solution": details.get("status"),
        }

        link = details.get("link")
        if link:
            # url can't be None
            vulnerability["identifiers"][0]["url"] = link
            vulnerability["links"] = [
                {
                    "url": link,
                }
            ]

        return vulnerability

    def _create_license_vulnerability(self, record: Record) -> dict[str, Any] | None:
        details = record.vulnerability_details
        if not details:
            # this shouldn't happen
            return None

        return {
            "id": str(uuid4()),
            "identifiers": [
                {
                    "name": record.check_id,
                    "type": "license",
                    "value": record.check_id,
                }
            ],
            "location": {
                "file": record.repo_file_path.lstrip("/"),
            },
            "name": record.short_description,
            "description": f"Package {details['package_name']}@{details['package_version']} has license {details['license']}",
        }
