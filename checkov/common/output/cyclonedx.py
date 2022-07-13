from __future__ import annotations

import itertools
import os
import sys
from typing import TYPE_CHECKING

from cyclonedx.model import XsUri, ExternalReference, ExternalReferenceType, sha1sum, HashAlgorithm, HashType
from cyclonedx.model.bom import Bom, Tool
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.vulnerability import Vulnerability, VulnerabilityAdvisory, BomTarget
from cyclonedx.output import SchemaVersion, get_instance
from packageurl import PackageURL  # type:ignore[import]

if sys.version_info >= (3, 8):
    from importlib.metadata import version as meta_version
else:
    from importlib_metadata import version as meta_version

if TYPE_CHECKING:
    from checkov.common.output.extra_resource import ExtraResource
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report

DEFAULT_CYCLONE_SCHEMA_VERSION = SchemaVersion.V1_4
CYCLONE_SCHEMA_VERSION: dict[str, SchemaVersion] = {
    "1.4": DEFAULT_CYCLONE_SCHEMA_VERSION,
    "1.3": SchemaVersion.V1_3,
    "1.2": SchemaVersion.V1_2,
    "1.1": SchemaVersion.V1_1,
    "1.0": SchemaVersion.V1_0,
}


class CycloneDX:
    def __init__(self, reports: list[Report]) -> None:
        self.reports = reports

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

        for report in self.reports:
            for check in itertools.chain(report.passed_checks, report.skipped_checks):
                component = self.create_component(check_type=report.check_type, resource=check)

                if not bom.has_component(component=component):
                    bom.components.add(component)

            for check in report.failed_checks:
                component = self.create_component(check_type=report.check_type, resource=check)

                if bom.has_component(component=component):
                    component = bom.get_component_by_purl(  # type:ignore[assignment]  # the previous line checks, if exists
                        purl=component.purl
                    )

                if check.guideline:
                    vulnerability = Vulnerability(
                        id=check.check_id,
                        source_name="checkov",
                        description=f"Resource: {check.resource}. {check.check_name}",
                        affects_targets=[BomTarget(ref=component.bom_ref.value)],
                        advisories=[VulnerabilityAdvisory(url=XsUri(check.guideline))],
                    )
                else:
                    vulnerability = Vulnerability(
                        id=check.check_id,
                        source_name="checkov",
                        description=f"Resource: {check.resource}. {check.check_name}",
                        affects_targets=[BomTarget(ref=component.bom_ref.value)],
                    )

                component.add_vulnerability(vulnerability)
                bom.components.add(component)

            for resource in report.extra_resources:
                component = self.create_component(check_type=report.check_type, resource=resource)

                if not bom.has_component(component=component):
                    bom.components.add(component)

        return bom

    def create_component(self, check_type: str, resource: Record | ExtraResource) -> Component:
        """ Creates a component

        Ex.
        <component bom-ref="pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a" type="file">
          <name>aws_s3_bucket.example</name>
          <version>sha1:92911b13224706178dded562c18d281b22bf391a</version>
          <hashes>
            <hash alg="SHA-1">92911b13224706178dded562c18d281b22bf391a</hash>
          </hashes>
          <purl>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</purl>
        </component>
        """

        sha1_hash = sha1sum(filename=resource.file_abs_path)
        purl = PackageURL(
            type=check_type,
            namespace=resource.file_path,
            name=resource.resource,
            version=f"sha1:{sha1_hash}",
        )
        component = Component(
            bom_ref=str(purl),
            name=resource.resource,
            version=f"sha1:{sha1_hash}",
            hashes=[
                HashType(
                    algorithm=HashAlgorithm.SHA_1,
                    hash_value=sha1_hash,
                )
            ],
            component_type=ComponentType.APPLICATION,
            purl=purl,
        )

        return component

    def get_xml_output(self) -> str:
        schema_version = CYCLONE_SCHEMA_VERSION.get(
            os.getenv("CHECKOV_CYCLONEDX_SCHEMA_VERSION", ""), DEFAULT_CYCLONE_SCHEMA_VERSION
        )
        output = get_instance(bom=self.bom, schema_version=schema_version).output_as_string()

        return output
