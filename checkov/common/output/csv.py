from __future__ import annotations

import csv
import itertools
import logging
import os
from datetime import datetime
from typing import Any, TYPE_CHECKING

from checkov.common.models.enums import CheckResult
from checkov.common.output.common import format_string_to_licenses, is_raw_formatted, validate_lines
from checkov.common.output.record import Record, SCA_PACKAGE_SCAN_CHECK_NAME
from checkov.common.output.report import Report, CheckType
from checkov.common.sca.commons import get_fix_version, UNFIXABLE_VERSION

if TYPE_CHECKING:
    from checkov.common.output.extra_resource import ExtraResource

date_now = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}'
FILE_NAME_OSS_PACKAGES = f"{date_now}_oss_packages.csv"
HEADER_OSS_PACKAGES = [
    "Package",
    "Version",
    "Path",
    "Line(s)",
    "Git Org",
    "Git Repository",
    "Vulnerability",
    "Severity",
    "Description",
    "Licenses",
    "Fix Version",
    "Registry URL",
    "Root Package",
    "Root Version"
]

HEADER_CONTAINER_IMAGE = HEADER_OSS_PACKAGES
FILE_NAME_CONTAINER_IMAGES = f"{date_now}_container_images.csv"

FILE_NAME_IAC = f"{date_now}_iac.csv"
HEADER_IAC = ["Resource", "Path", "Git Org", "Git Repository", "Misconfigurations", "Severity", "Policy title", "Guideline"]

CTA_NO_API_KEY = "SCA, image and runtime findings are only available with a Prisma Cloud subscription."


class CSVSBOM:
    def __init__(self) -> None:
        self.iac_rows: list[dict[str, Any]] = []
        self.container_rows: list[dict[str, Any]] = []
        self.package_rows: list[dict[str, Any]] = []

        self.iac_rows_have_details: bool = False

        self.iac_resource_cache: set[str] = set()  # used to check, if a resource was already added

    def add_report(self, report: Report, git_org: str, git_repository: str) -> None:
        if report.check_type in (CheckType.SCA_PACKAGE, CheckType.SCA_IMAGE):
            for record in itertools.chain(report.failed_checks, report.passed_checks, report.skipped_checks):
                if record.check_name == SCA_PACKAGE_SCAN_CHECK_NAME:
                    self.add_sca_package_resources(resource=record, git_org=git_org, git_repository=git_repository, check_type=report.check_type)
            for resource in sorted(report.extra_resources):
                self.add_sca_package_resources(resource=resource, git_org=git_org, git_repository=git_repository, check_type=report.check_type)
        else:
            for record in itertools.chain(report.failed_checks, report.passed_checks, report.skipped_checks):
                self.add_iac_resources(resource=record, git_org=git_org, git_repository=git_repository)
            for resource in sorted(report.extra_resources):
                self.add_iac_resources(resource=resource, git_org=git_org, git_repository=git_repository)

    def add_sca_package_resources(self, resource: Record | ExtraResource, git_org: str, git_repository: str, check_type: str) -> None:
        if not resource.vulnerability_details:
            # this shouldn't happen
            logging.error(f"Resource {resource.resource} doesn't have 'vulnerability_details' set")
            return

        severity = None
        if isinstance(resource, Record) and resource.severity is not None:
            # ExtraResource don't have a CVE/Severity
            severity = resource.severity.name
        csv_table = {
            CheckType.SCA_PACKAGE: self.package_rows,
            CheckType.SCA_IMAGE: self.container_rows
        }

        lines = resource.file_line_range
        lines = validate_lines(lines)
        fix_version = self.get_fix_version_overview(resource.vulnerability_details)
        csv_table[check_type].append(
            {
                "Package": resource.vulnerability_details["package_name"],
                "Version": resource.vulnerability_details["package_version"],
                "Path": resource.file_path,
                "Line(s)": lines,
                "Git Org": git_org,
                "Git Repository": git_repository,
                "Vulnerability": resource.vulnerability_details.get("id"),
                "Severity": severity,
                "Description": resource.vulnerability_details.get("description"),
                "Licenses": resource.vulnerability_details.get("licenses"),
                "Fix Version": fix_version,
                "Registry URL": resource.vulnerability_details.get("package_registry"),
                "Root Package": resource.vulnerability_details.get("root_package_name"),
                "Root Version": resource.vulnerability_details.get("root_package_version")
            }
        )

    def get_fix_version_overview(self, vulnerability_details: dict[str, Any]) -> str:
        is_private_fix = vulnerability_details.get("is_private_fix")
        public_fix_version_suffix = " (Public)" if is_private_fix is False else ""
        fix_version: str = get_fix_version(vulnerability_details)
        return fix_version + public_fix_version_suffix if fix_version and fix_version != UNFIXABLE_VERSION else fix_version

    def add_iac_resources(self, resource: Record | ExtraResource, git_org: str, git_repository: str) -> None:
        resource_id = f"{git_org}/{git_repository}/{resource.file_path}/{resource.resource}"

        misconfig = None
        severity = None
        check_name = None
        guideline = None
        if isinstance(resource, Record) and resource.check_result["result"] == CheckResult.FAILED:
            # only failed resources should be added with their misconfiguration
            misconfig = resource.check_id
            if resource.severity is not None:
                severity = resource.severity.name
            check_name = resource.check_name
            guideline = resource.guideline
        elif resource_id in self.iac_resource_cache:
            # IaC resources shouldn't be added multiple times, if they don't have any misconfiguration
            return

        row = {
            "Resource": resource.resource,
            "Path": resource.file_path,
            "Git Org": git_org,
            "Git Repository": git_repository,
            "Misconfigurations": misconfig,
            "Severity": severity,
            "Policy title": check_name,
            "Guideline": guideline
        }

        if isinstance(resource, Record) and resource.details:
            self.iac_rows_have_details = True
            row["Details"] = "|".join(resource.details)

        self.iac_rows.append(row)
        self.iac_resource_cache.add(resource_id)

    def persist_report(self, is_api_key: bool, output_path: str = "") -> None:
        output_path = output_path or ""

        self.persist_report_iac(file_name=FILE_NAME_IAC, output_path=output_path)
        self.persist_report_container_images(
            file_name=FILE_NAME_CONTAINER_IMAGES,
            is_api_key=is_api_key,
            output_path=output_path,
        )
        self.persist_report_oss_packages(
            file_name=FILE_NAME_OSS_PACKAGES,
            is_api_key=is_api_key,
            output_path=output_path,
        )

    def persist_report_iac(self, file_name: str, output_path: str = "") -> None:
        CSVSBOM.write_section(
            file=os.path.join(output_path, file_name),
            header=[*HEADER_IAC, "Details"] if self.iac_rows_have_details else HEADER_IAC,
            rows=self.iac_rows,
            is_api_key=True,
        )

    def persist_report_container_images(self, file_name: str, is_api_key: bool, output_path: str = "") -> None:
        CSVSBOM.write_section(
            file=os.path.join(output_path, file_name),
            header=HEADER_CONTAINER_IMAGE,
            rows=self.container_rows,
            is_api_key=is_api_key,
        )

    def persist_report_oss_packages(self, file_name: str, is_api_key: bool, output_path: str = "") -> None:
        CSVSBOM.write_section(
            file=os.path.join(output_path, file_name),
            header=HEADER_OSS_PACKAGES,
            rows=self.package_rows,
            is_api_key=is_api_key,
        )

    @staticmethod
    def arrange_rows(rows: list[dict[str, Any]]) -> None:
        # we search for formatted rows and convert them back into csv formatted file.
        for row in rows:
            for key, value in row.items():
                val = str(value)

                if is_raw_formatted(val):
                    val = ', '.join(format_string_to_licenses(val))
                val = val[1:-1] if val.startswith('"') and val.endswith('"') else val
                row[key] = '' if val == 'None' else val

    @staticmethod
    def write_section(file: str, header: list[str], rows: list[dict[str, Any]], is_api_key: bool) -> None:
        CSVSBOM.arrange_rows(rows)

        with open(file, "w", newline="") as f:
            logging.info(f"Persisting SBOM to {os.path.abspath(file)}")
            if is_api_key:
                dict_writer = csv.DictWriter(f, fieldnames=header)
                dict_writer.writeheader()
                dict_writer.writerows(rows)
            else:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerow([CTA_NO_API_KEY])

    def get_csv_output_packages(self, check_type: str) -> str:
        # header
        csv_output = ','.join(HEADER_OSS_PACKAGES) + '\n'
        csv_table = {
            CheckType.SCA_PACKAGE: self.package_rows,
            CheckType.SCA_IMAGE: self.container_rows
        }

        for row in csv_table[check_type]:
            for header in HEADER_OSS_PACKAGES:
                field = row[header] if row[header] else ''
                if header == 'Package':
                    csv_output += f'\"{field}\"'
                elif header == 'Description':
                    csv_output += f',\"{field}\"'
                elif header == 'Licenses':
                    field = str(field).replace('","', ", ")
                    field = field[1:-1] if field.startswith('"') and field.endswith('"') else field
                    csv_output += f',\"{field}\"'
                else:
                    csv_output += f',{field}'
            csv_output += '\n'

        return csv_output
