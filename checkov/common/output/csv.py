from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Any

from checkov.common.output.report import Report, CheckType

date_now = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}'
FILE_NAME_OSS_PACKAGES = f'{date_now}_oss_packages.csv'
HEADER_OSS_PACKAGES = ["Package", "Version", "Path", "git org", "git repository", "Vulnerability", "Severity",
                       "License"]
HEADER_CONTAINER_IMAGE = HEADER_OSS_PACKAGES
FILE_NAME_CONTAINER_IMAGES = f'{date_now}_container_images.csv'

FILE_NAME_IAC = f'{date_now}_iac.csv'
HEADER_IAC = ["Resource", "Path", "git org", "git repository", "Misconfigurations", "Severity"]

CTA_NO_API_KEY = "SCA, image and runtime findings are only available with Bridgecrew. Signup at " \
                 "https://www.bridgecrew.cloud/login/signUp and add your API key to include those findings. "


class CSVSBOM():

    def __init__(self) -> None:
        self.iac_rows: list[dict[str, Any]] = []
        self.container_rows: list[dict[str, Any]] = []
        self.package_rows: list[dict[str, Any]] = []

    def add_report(self, report: Report, git_org: str, git_repository: str) -> None:
        if report.check_type != CheckType.SCA_IMAGE and report.check_type != CheckType.SCA_PACKAGE:
            for failed_record in report.failed_checks:
                self.iac_rows.append(
                    {"Resource": failed_record.resource, "Path": failed_record.file_path, "git org": git_org,
                     "git repository": git_repository, "Misconfigurations": failed_record.check_id,
                     "Severity": failed_record.severity})
            for extra_resource in report.extra_resources:
                self.iac_rows.append(
                    {"Resource": extra_resource.resource, "Path": extra_resource.file_path, "git org": git_org,
                     "git repository": git_repository, "Misconfigurations": "",
                     "Severity": ""})

    def persist_report(self, is_api_key: bool, output_path: str = "") -> None:
        self.persist_report_iac(file_name=FILE_NAME_IAC, output_path=output_path)
        self.persist_report_container_images(file_name=FILE_NAME_CONTAINER_IMAGES, is_api_key=is_api_key, output_path=output_path)
        self.persist_report_oss_packages(file_name=FILE_NAME_OSS_PACKAGES, is_api_key=is_api_key, output_path=output_path)

    def persist_report_iac(self, file_name: str, output_path: str = "") -> None:
        CSVSBOM.write_section(file=os.path.join(output_path, file_name), header=HEADER_IAC, rows=self.iac_rows,
                              is_api_key=True)

    def persist_report_container_images(self, file_name: str, is_api_key: bool, output_path: str = "") -> None:
        CSVSBOM.write_section(file=os.path.join(output_path, file_name), header=HEADER_CONTAINER_IMAGE,
                              rows=self.container_rows, is_api_key=is_api_key)

    def persist_report_oss_packages(self, file_name: str, is_api_key: bool, output_path: str = "") -> None:
        CSVSBOM.write_section(file=os.path.join(output_path, file_name), header=HEADER_OSS_PACKAGES,
                              rows=self.package_rows, is_api_key=is_api_key)

    @staticmethod
    def write_section(file: str, header: list[str], rows: list[dict[str, Any]], is_api_key: bool) -> None:
        with open(file, 'w', newline='') as f:
            print(f'Persisting SBOM to {os.path.abspath(file)}')
            if is_api_key:
                dict_writer = csv.DictWriter(f, fieldnames=header)
                dict_writer.writeheader()
                dict_writer.writerows(rows)
            else:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerow([CTA_NO_API_KEY])
