import csv
from datetime import datetime

from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType

my_date = datetime.now()
scan_date = f', Scan Date: {my_date.isoformat()}'
TITLE_OSS_PACKAGES = f'Open Source Packages {scan_date}'
HEADER_OSS_PACKAGES = ["Package", "Version", "Path", "git org", "git repository", "Vulnerability", "Severity",
                       "License"]
HEADER_CONTAINER_IMAGE = HEADER_OSS_PACKAGES
TITLE_CONTAINER_IMAGE = f'Container image {scan_date}'

TITLE_IAC = f"Infrastructure as Code Components {scan_date} "
HEADER_IAC = ["Resource", "Path", "git org", "git repository", "Misconfigurations", "Severity"]


class CSVSBOM():
    def __init__(self) -> None:
        self.iac_rows = []
        self.container_rows = []
        self.package_rows = []

    def add_report(self, report: Report, git_org, git_repository):
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

    def persist_report(self, path: str):
        with open(path, 'w', newline='') as file:
            CSVSBOM.write_section(file=file, title=TITLE_OSS_PACKAGES, header=HEADER_OSS_PACKAGES,
                                  rows=self.package_rows)
            CSVSBOM.write_section(file=file, title=TITLE_CONTAINER_IMAGE, header=HEADER_CONTAINER_IMAGE,
                                  rows=self.container_rows)
            CSVSBOM.write_section(file=file, title=TITLE_IAC, header=HEADER_IAC,
                                  rows=self.iac_rows)

    @staticmethod
    def write_section(file, title, header, rows):
        writer = csv.DictWriter(file, fieldnames=[title])
        writer.writeheader()
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
        writer = csv.DictWriter(file, fieldnames='')
        writer.writeheader()
