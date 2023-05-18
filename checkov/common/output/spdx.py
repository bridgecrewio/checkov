from __future__ import annotations
import itertools
import logging

from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.record import SCA_PACKAGE_SCAN_CHECK_NAME, Record
from license_expression import get_spdx_licensing

from io import StringIO

from spdx.creationinfo import Tool, Organization
from spdx.document import Document
from spdx.license import License
from spdx.package import Package
from spdx.writers.tagvalue import write_document

from checkov.common.output.cyclonedx_consts import SCA_CHECKTYPES
from checkov.common.output.report import Report

DOCUMENT_NAME = "checkov-sbom"
SPDXREF = "SPDXRef-"


class SPDX:
    def __init__(self, repo_id: str | None, reports: list[Report]):
        self.repo_id = f"{repo_id}/" if repo_id else ""
        self.reports = reports

        self.document = self.create_document()

    def create_document(self) -> Document:
        document = Document(
            version="SPDX2.3",
            data_license=License.from_identifier(identifier="CC0-1.0"),
            name=DOCUMENT_NAME,
            spdx_id="SPDXRef-DOCUMENT",
            namespace=f"{self.repo_id}{DOCUMENT_NAME}",
        )
        document.creation_info.set_created_now()
        document.creation_info.add_creator(Tool(name="checkov"))
        document.creation_info.add_creator(Organization(name="bridgecrew"))

        return document

    def get_tag_value_output(self) -> str:
        output = StringIO()

        self.add_packages_to_doc()
        write_document(document=self.document, out=output, validate=True)  # later set to True

        return output.getvalue()

    def validate_licenses(self, package: Package, license_: str) -> None:
        if license_ and license_ not in ['Unknown license', 'NOT_FOUND', 'Unknown']:
            split_licenses = license_.split(",")
            licenses = []

            for lic in split_licenses:
                lic = lic.strip('"')
                try:
                    is_spdx_license = License(get_spdx_licensing().parse(lic), lic)
                    licenses.append(is_spdx_license)
                except Exception as e:
                    logging.info(f"error occured when trying to parse the license:{split_licenses} due to error {e}")
            package.licenses_from_files = licenses

    def create_package(self, check: Record | ExtraResource) -> Package:
        package_data = check.vulnerability_details
        if not package_data:
            # this shouldn't happen
            logging.error(f"Check {check.resource} doesn't have 'vulnerability_details' set")
            return Package(name="unknown")

        package_name = package_data.get('package_name')
        package = Package(
            name=package_name,
            spdx_id=f"{SPDXREF}{package_name}",
            version=package_data['package_version'],
            download_location='N/A',
            file_name=check.file_path
        )
        license_ = package_data.get('licenses', "")
        self.validate_licenses(package=package, license_=license_)

        return package

    def add_packages_to_doc(self) -> None:
        packages_set = set()
        for report in self.reports:
            for check in itertools.chain(report.passed_checks, report.skipped_checks):
                if report.check_type in SCA_CHECKTYPES and check.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                    continue
                package = self.create_package(check)
                if package not in packages_set:
                    packages_set.add(package)

            for check in report.failed_checks:
                if report.check_type in SCA_CHECKTYPES and check.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                    continue
                package = self.create_package(check)
                if package not in packages_set:
                    packages_set.add(package)

            for resource in sorted(report.extra_resources):
                package = self.create_package(resource)
                if package not in packages_set:
                    packages_set.add(package)

        if packages_set:
            self.document.packages = list(packages_set)
