from __future__ import annotations

import itertools
import logging
from datetime import datetime, timezone
from io import StringIO
from typing import TYPE_CHECKING
from uuid import uuid4

from license_expression import get_spdx_licensing
from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.document import Document, CreationInfo
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.model.spdx_none import SpdxNone
from spdx_tools.spdx.writer.tagvalue.tagvalue_writer import write_document

from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.record import SCA_PACKAGE_SCAN_CHECK_NAME, Record
from checkov.common.output.cyclonedx_consts import SCA_CHECKTYPES
from checkov.common.output.report import Report
from checkov.version import version

if TYPE_CHECKING:
    from boolean import Expression as LicenseExpression
    from spdx_tools.spdx.model import SpdxNoAssertion


DOCUMENT_NAME = "checkov-sbom"
SPDXREF = "SPDXRef-"


class SPDX:
    def __init__(self, repo_id: str | None, reports: list[Report]):
        self.repo_id = f"{repo_id}/" if repo_id else ""
        self.reports = reports

        self.document = self.create_document()
        self.packages: list[Package] = []

        # each entry looks like '{file_name}#{package_name}#{package_version}'
        self._added_packages_cache: set[str] = set()

    def create_document(self) -> Document:
        creation_info = CreationInfo(
            spdx_version="SPDX-2.3",
            spdx_id="SPDXRef-DOCUMENT",
            name=DOCUMENT_NAME,
            data_license="CC0-1.0",
            document_namespace=f"https://spdx.org/spdxdocs/{DOCUMENT_NAME}-{version}-{uuid4()}",
            creators=[
                Actor(ActorType.TOOL, "checkov"),
                Actor(ActorType.ORGANIZATION, "bridgecrew", "meet@bridgecrew.io"),
            ],
            created=datetime.now(timezone.utc),
        )
        return Document(creation_info=creation_info)

    def get_tag_value_output(self) -> str:
        output = StringIO()

        self.add_packages_to_doc()
        write_document(document=self.document, text_output=output)

        return output.getvalue()

    def validate_licenses(self, package: Package, license_: str) -> None:
        if license_ and license_ not in ["Unknown license", "NOT_FOUND", "Unknown"]:
            split_licenses = license_.split(",")
            licenses: list[LicenseExpression | SpdxNoAssertion | SpdxNone] = []

            for lic in split_licenses:
                lic = lic.strip('"')
                try:
                    license_expression = get_spdx_licensing().parse(lic)
                    if license_expression is not None:
                        licenses.append(license_expression)
                except Exception as e:
                    logging.info(f"error occurred when trying to parse the license:{split_licenses} due to error {e}")
            package.license_info_from_files = licenses

    def create_package(self, check: Record | ExtraResource) -> Package:
        package_data = check.vulnerability_details
        if not package_data:
            # this shouldn't happen
            logging.error(f"Check {check.resource} doesn't have 'vulnerability_details' set")
            return Package(name="unknown", spdx_id=f"{SPDXREF}unknown", download_location=SpdxNone())

        package_name = package_data.get("package_name")
        if not package_name:
            # this shouldn't happen
            logging.error(f"Package {package_data} doesn't have 'package_name' set")
            return Package(name="unknown", spdx_id=f"{SPDXREF}unknown", download_location=SpdxNone())

        package = Package(
            name=package_name,
            spdx_id=f"{SPDXREF}{package_name}",
            version=package_data["package_version"],
            download_location=SpdxNone(),
            file_name=check.file_path,
        )
        license_ = package_data.get("licenses", "")
        self.validate_licenses(package=package, license_=license_)

        return package

    def add_packages_to_doc(self) -> None:
        for report in self.reports:
            for check in itertools.chain(report.passed_checks, report.skipped_checks):
                if report.check_type in SCA_CHECKTYPES and check.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                    continue
                package = self.create_package(check)
                self.add_new_package_to_list(package)

            for check in report.failed_checks:
                if report.check_type in SCA_CHECKTYPES and check.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                    continue
                package = self.create_package(check)
                self.add_new_package_to_list(package)

            for resource in sorted(report.extra_resources):
                package = self.create_package(resource)
                self.add_new_package_to_list(package)

        if self.packages:
            self.document.packages = self.packages

    def add_new_package_to_list(self, package: Package) -> None:
        """Adds a package to the list, if it not exists"""

        package_cache_entry = f"{package.file_name}#{package.name}#{package.version}"
        if package_cache_entry not in self._added_packages_cache:
            self.packages.append(package)
            self._added_packages_cache.add(package_cache_entry)
