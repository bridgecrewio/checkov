from __future__ import annotations

import itertools
import os
import sys
from typing import TYPE_CHECKING

from cyclonedx.model import XsUri, ExternalReference, ExternalReferenceType
from cyclonedx.model.bom import Bom, Tool
from cyclonedx.model.component import Component
from cyclonedx.model.vulnerability import Vulnerability, VulnerabilityAdvisory
from cyclonedx.output import SchemaVersion, get_instance

if sys.version_info >= (3, 8):
    from importlib.metadata import version as meta_version
else:
    from importlib_metadata import version as meta_version

if TYPE_CHECKING:
    from checkov.common.output.record import Record

DEFAULT_CYCLONE_SCHEMA_VERSION = SchemaVersion.V1_4
CYCLONE_SCHEMA_VERSION: dict[str, SchemaVersion] = {
    "1.4": DEFAULT_CYCLONE_SCHEMA_VERSION,
    "1.3": SchemaVersion.V1_3,
    "1.2": SchemaVersion.V1_2,
    "1.1": SchemaVersion.V1_1,
    "1.0": SchemaVersion.V1_0,
}


class CycloneDX:
    def __init__(self, passed_checks: list[Record], failed_checks: list[Record], skipped_checks: list[Record]) -> None:
        self.passed_checks = passed_checks
        self.failed_checks = failed_checks
        self.skipped_checks = skipped_checks

        self.bom = self.create_bom()

    def create_bom(self) -> Bom:
        bom = Bom()

        try:
            version = meta_version("checkov")  # type:ignore[no-untyped-call]  # issue between Python versions
        except Exception:
            # Unable to determine current version of 'checkov'
            version = "UNKNOWN"

        this_tool = Tool(vendor="bridgecrew", name="checkov", version=version)
        this_tool.external_references.update(
            [
                ExternalReference(
                    reference_type=ExternalReferenceType.BUILD_SYSTEM,
                    url=XsUri("https://github.com/bridgecrewio/checkov/actions"),
                ),
                ExternalReference(
                    reference_type=ExternalReferenceType.DISTRIBUTION,
                    url=XsUri("https://pypi.org/project/checkov/"),
                ),
                ExternalReference(
                    reference_type=ExternalReferenceType.DOCUMENTATION,
                    url=XsUri("https://www.checkov.io/1.Welcome/What%20is%20Checkov.html"),
                ),
                ExternalReference(
                    reference_type=ExternalReferenceType.ISSUE_TRACKER,
                    url=XsUri("https://github.com/bridgecrewio/checkov/issues"),
                ),
                ExternalReference(
                    reference_type=ExternalReferenceType.LICENSE,
                    url=XsUri("https://github.com/bridgecrewio/checkov/blob/master/LICENSE"),
                ),
                ExternalReference(
                    reference_type=ExternalReferenceType.SOCIAL,
                    url=XsUri("https://twitter.com/bridgecrewio"),
                ),
                ExternalReference(
                    reference_type=ExternalReferenceType.VCS,
                    url=XsUri("https://github.com/bridgecrewio/checkov"),
                ),
                ExternalReference(
                    reference_type=ExternalReferenceType.WEBSITE,
                    url=XsUri("https://www.checkov.io/"),
                ),
            ]
        )

        bom.metadata.tools.add(this_tool)

        for check in itertools.chain(self.passed_checks, self.skipped_checks):
            component = Component.for_file(absolute_file_path=check.file_abs_path, path_for_bom=check.file_path)

            if bom.has_component(component=component):
                component = bom.get_component_by_purl(  # type:ignore[assignment]  # the previous line checks, if exists
                    purl=component.purl
                )

            bom.components.add(component)

        for failed_check in self.failed_checks:
            component = Component.for_file(
                absolute_file_path=failed_check.file_abs_path, path_for_bom=failed_check.file_path
            )

            if bom.has_component(component=component):
                component = bom.get_component_by_purl(  # type:ignore[assignment]  # the previous line checks, if exists
                    purl=component.purl
                )

            if failed_check.guideline:
                vulnerability = Vulnerability(
                    id=failed_check.check_id,
                    source_name="checkov",
                    description=f"Resource: {failed_check.resource}. {failed_check.check_name}",
                    advisories=[VulnerabilityAdvisory(url=XsUri(failed_check.guideline))],
                )
            else:
                vulnerability = Vulnerability(
                    id=failed_check.check_id,
                    source_name="checkov",
                    description=f"Resource: {failed_check.resource}. {failed_check.check_name}",
                )

            component.add_vulnerability(vulnerability)
            bom.components.add(component)

        return bom

    def get_xml_output(self) -> str:
        schema_version = CYCLONE_SCHEMA_VERSION.get(
            os.getenv("CHECKOV_CYCLONEDX_SCHEMA_VERSION", ""), DEFAULT_CYCLONE_SCHEMA_VERSION
        )
        outputter = get_instance(bom=self.bom, schema_version=schema_version)

        return outputter.output_as_string()
