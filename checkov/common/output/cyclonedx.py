from __future__ import annotations

import itertools
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast, Any
from checkov.common.output.common import format_string_to_licenses

from cyclonedx.model import (
    XsUri,
    ExternalReference,
    ExternalReferenceType,
    sha1sum,
    HashAlgorithm,
    HashType,
    LicenseChoice,
    License,
)
from cyclonedx.model.bom import Bom, Tool
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.vulnerability import (
    Vulnerability,
    VulnerabilityAdvisory,
    BomTarget,
    VulnerabilitySource,
    VulnerabilityRating,
    VulnerabilityScoreSource,
    VulnerabilitySeverity,
)
from cyclonedx.output import get_instance, OutputFormat
from packageurl import PackageURL

from checkov.common.output.common import ImageDetails
from checkov.common.output.report import CheckType
from checkov.common.output.cyclonedx_consts import (
    SCA_CHECKTYPES,
    PURL_TYPE_MAVEN,
    DEFAULT_CYCLONE_SCHEMA_VERSION,
    CYCLONE_SCHEMA_VERSION,
    FILE_NAME_TO_PURL_TYPE,
    IMAGE_DISTRO_TO_PURL_TYPE,
    TWISTCLI_PACKAGE_TYPE_TO_PURL_TYPE,
    BC_SEVERITY_TO_CYCLONEDX_LEVEL,
)
from checkov.common.output.record import SCA_PACKAGE_SCAN_CHECK_NAME

if sys.version_info >= (3, 8):
    from importlib.metadata import version as meta_version
else:
    from importlib_metadata import version as meta_version

if TYPE_CHECKING:
    from checkov.common.output.extra_resource import ExtraResource
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report


class CycloneDX:
    def __init__(self, reports: list[Report], repo_id: str | None, export_iac_only: bool = False) -> None:
        self.repo_id = f"{repo_id}/" if repo_id is not None else ""
        self.reports = reports
        self.export_iac_only = export_iac_only

        self.bom = self.create_bom()

    def create_bom(self) -> Bom:
        bom = Bom()

        try:
            version = meta_version("checkov")  # type:ignore[no-untyped-call]
        except Exception:
            # Unable to determine current version of 'checkov'
            version = "UNKNOWN"

        this_tool = Tool(vendor="bridgecrew", name="checkov", version=version)
        self.update_tool_external_references(this_tool)
        bom.metadata.tools.add(this_tool)

        for report in self.reports:
            if report.check_type in SCA_CHECKTYPES and self.export_iac_only:
                continue

            # if the report is of SCA_IMAGE type, we should add to the report one image component per image
            is_image_report = report.check_type == CheckType.SCA_IMAGE
            image_resources_for_image_components = {}

            for check in itertools.chain(report.passed_checks, report.skipped_checks):
                if report.check_type in SCA_CHECKTYPES and check.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                    continue
                component = self.create_component(check_type=report.check_type, resource=check)

                if not bom.has_component(component=component):
                    bom.components.add(component)

                if is_image_report and check.file_path not in image_resources_for_image_components:
                    image_resources_for_image_components[check.file_path] = check

            for check in report.failed_checks:
                if report.check_type in SCA_CHECKTYPES and check.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                    continue
                component = self.create_component(check_type=report.check_type, resource=check)

                if bom.has_component(component=component):
                    component = (
                        bom.get_component_by_purl(  # type:ignore[assignment]  # the previous line checks, if exists
                            purl=component.purl
                        )
                    )

                vulnerability = self.create_vulnerability(
                    check_type=report.check_type, resource=check, component=component
                )

                component.add_vulnerability(vulnerability)
                bom.components.add(component)

                if is_image_report:
                    if check.file_path not in image_resources_for_image_components:
                        image_resources_for_image_components[check.file_path] = check

            for resource in sorted(report.extra_resources):
                component = self.create_component(check_type=report.check_type, resource=resource)

                if not bom.has_component(component=component):
                    bom.components.add(component)

            if is_image_report:
                for image_resource in image_resources_for_image_components:
                    self.create_image_component(resource=image_resources_for_image_components[image_resource], bom=bom)

        return bom

    def create_component(self, check_type: str, resource: Record | ExtraResource) -> Component:
        """Creates a component"""
        # purl structure conventions: https://github.com/package-url/purl-spec/blob/master/PURL-TYPES.rst

        if check_type in SCA_CHECKTYPES:
            component = self.create_library_component(check_type=check_type, resource=resource)
        else:
            component = self.create_application_component(check_type=check_type, resource=resource)

        return component

    def create_application_component(self, check_type: str, resource: Record | ExtraResource) -> Component:
        """Creates an application component
        Ex.
        <component bom-ref="pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85" type="application">
          <name>aws_s3_bucket.example</name>
          <version>sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</version>
          <hashes>
            <hash alg="SHA-1">c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</hash>
          </hashes>
          <purl>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</purl>
        </component>
        """

        sha1_hash = sha1sum(filename=resource.file_abs_path)
        purl = PackageURL(
            type=check_type,
            namespace=f"{self.repo_id}/{resource.file_path}",
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

    def create_library_component(self, resource: Record | ExtraResource, check_type: str) -> Component:
        """Creates a library component
        Ex.
        <component bom-ref="pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6" type="library">
          <name>flask</name>
          <version>0.6</version>
          <purl>pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6</purl>
        </component>
        """

        if not resource.vulnerability_details:
            # this shouldn't happen
            logging.error(f"Resource {resource.resource} doesn't have 'vulnerability_details' set")
            return Component(name="unknown")
        qualifiers = None
        file_name = Path(resource.file_path).name
        if check_type is CheckType.SCA_IMAGE:
            package_type = resource.vulnerability_details['package_type']
            image_distro_name = resource.vulnerability_details.get('image_details', ImageDetails()).distro.split(' ')[0]
            file_path = resource.file_path.split(' ')[0]
            if package_type == 'os':
                purl_type = IMAGE_DISTRO_TO_PURL_TYPE.get(image_distro_name, 'generic')
                namespace = f'{self.repo_id}/{file_path}/{image_distro_name.lower()}'
                qualifiers = f'distro={resource.vulnerability_details.get("image_details", ImageDetails()).distro_release}'
            else:
                purl_type = TWISTCLI_PACKAGE_TYPE_TO_PURL_TYPE.get(package_type, 'generic')
                namespace = f"{self.repo_id}/{file_path}"
        else:
            purl_type = FILE_NAME_TO_PURL_TYPE.get(file_name, "generic")
            namespace = f"{self.repo_id}/{resource.file_path}"
        package_group = None
        package_name = resource.vulnerability_details["package_name"]
        package_version = resource.vulnerability_details["package_version"]

        if purl_type == PURL_TYPE_MAVEN and "_" in package_name:
            package_group, package_name = package_name.split("_", maxsplit=1)
            namespace += f"/{package_group}"

        # add licenses, if exists
        license_choices = None
        licenses = resource.vulnerability_details.get("licenses")
        if licenses:
            license_choices = [
                LicenseChoice(license_=License(license_name=license)) for license in format_string_to_licenses(licenses)
            ]

        purl = PackageURL(
            type=purl_type,
            namespace=namespace,
            name=package_name,
            version=package_version,
            qualifiers=qualifiers,
        )
        component = Component(
            bom_ref=str(purl),
            group=package_group,
            name=package_name,
            version=package_version,
            component_type=ComponentType.LIBRARY,
            licenses=license_choices,
            purl=purl,
        )
        return component

    def create_image_component(self, resource: Record, bom: Bom) -> None:
        image_id = cast("dict[str, Any]", resource.vulnerability_details).get('image_details', ImageDetails()).image_id
        file_path = resource.file_path.split(' ')[0]
        image_purl = PackageURL(
            type='oci',
            namespace=self.repo_id,
            name=file_path,
            version=image_id,
        )
        bom.components.add(
            Component(
                bom_ref=str(image_purl),
                component_type=ComponentType.CONTAINER,
                name=f"{self.repo_id}/{image_id}",
                version="",
                purl=image_purl,
            )
        )

    def create_vulnerability(self, check_type: str, resource: Record, component: Component) -> Vulnerability:
        """Creates a vulnerability"""

        if check_type in SCA_CHECKTYPES:
            vulnerability = self.create_cve_vulnerability(resource=resource, component=component)
        else:
            vulnerability = self.create_iac_vulnerability(resource=resource, component=component)

        return vulnerability

    def create_iac_vulnerability(self, resource: Record, component: Component) -> Vulnerability:
        """Creates a IaC based vulnerability
        Ex.
        <vulnerability bom-ref="41f657e7-a83b-4535-9b83-541211d02397">
          <id>CKV_AWS_21</id>
          <source>
            <name>checkov</name>
          </source>
          <ratings>
            <rating>
              <severity>medium</severity>
            </rating>
          </ratings>
          <description>Resource: aws_s3_bucket.example. Ensure all data stored in the S3 bucket have versioning enabled</description>
          <advisories>
            <advisory>
              <url>https://docs.bridgecrew.io/docs/s3_16-enable-versioning</url>
            </advisory>
          </advisories>
          <affects>
            <target>
              <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
            </target>
          </affects>
        </vulnerability>
        """

        advisories = None
        if resource.guideline:
            advisories = [VulnerabilityAdvisory(url=XsUri(resource.guideline))]

        severity = VulnerabilitySeverity.UNKNOWN
        if resource.severity:
            severity = BC_SEVERITY_TO_CYCLONEDX_LEVEL.get(resource.severity.name, VulnerabilitySeverity.UNKNOWN)

        vulnerability = Vulnerability(
            id=resource.check_id,
            source=VulnerabilitySource(name="checkov"),
            ratings=[
                VulnerabilityRating(
                    severity=severity,
                )
            ],
            description=f"Resource: {resource.resource}. {resource.check_name}",
            affects_targets=[BomTarget(ref=component.bom_ref.value)],
            advisories=advisories,
        )
        return vulnerability

    def create_cve_vulnerability(self, resource: Record, component: Component) -> Vulnerability:
        """Creates a CVE based vulnerability
        Ex.
        <vulnerability bom-ref="f18f3674-092f-4e9a-8452-641fd11fc70f">
          <id>CVE-2019-1010083</id>
          <source>
            <url>https://nvd.nist.gov/vuln/detail/CVE-2019-1010083</url>
          </source>
          <ratings>
            <rating>
              <source>
                <url>https://nvd.nist.gov/vuln/detail/CVE-2019-1010083</url>
              </source>
              <score>7.5</score>
              <severity>unknown</severity>
              <method>CVSSv3</method>
              <vector>AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H</vector>
            </rating>
          </ratings>
          <description>The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. ...</description>
          <recommendation>fixed in 1.0</recommendation>
          <published>2019-07-17T14:15:00</published>
          <affects>
            <target>
              <ref>pkg:pypi/flask@0.6</ref>
            </target>
          </affects>
        </vulnerability>
        """

        if not resource.vulnerability_details:
            # this shouldn't happen
            logging.error(f"Resource {resource.resource} doesn't have 'vulnerability_details' set")
            return Vulnerability()

        severity = VulnerabilitySeverity.UNKNOWN
        if resource.severity:
            severity = BC_SEVERITY_TO_CYCLONEDX_LEVEL.get(resource.severity.name, VulnerabilitySeverity.UNKNOWN)

        source = None
        source_url = resource.vulnerability_details.get("link")
        if source_url:
            source = VulnerabilitySource(url=source_url)
        method = None
        vector = resource.vulnerability_details["vector"]

        if vector:
            method = VulnerabilityScoreSource.get_from_vector(vector)
            vector = method.get_localised_vector(vector)

        vulnerability = Vulnerability(
            id=resource.vulnerability_details["id"],
            source=source,
            ratings=[
                VulnerabilityRating(
                    source=source,
                    score=resource.vulnerability_details.get("cvss"),
                    severity=severity,
                    method=method,
                    vector=vector,
                )
            ],
            description=resource.vulnerability_details.get("description"),
            recommendation=resource.vulnerability_details.get("status"),
            published=datetime.fromisoformat(resource.vulnerability_details["published_date"].replace("Z", "")),
            affects_targets=[BomTarget(ref=component.bom_ref.value)],
        )
        return vulnerability

    def get_output(self, output_format: OutputFormat) -> str:
        """Returns the SBOM as a formatted string"""

        schema_version = CYCLONE_SCHEMA_VERSION.get(
            os.getenv("CHECKOV_CYCLONEDX_SCHEMA_VERSION", ""), DEFAULT_CYCLONE_SCHEMA_VERSION
        )
        output = get_instance(
            bom=self.bom,
            output_format=output_format,
            schema_version=schema_version,
        ).output_as_string()

        return output

    def get_xml_output(self) -> str:
        """Returns the SBOM as a XML formatted string"""

        return self.get_output(output_format=OutputFormat.XML)

    def get_json_output(self) -> str:
        """Returns the SBOM as a JSON formatted string"""

        return self.get_output(output_format=OutputFormat.JSON)

    def update_tool_external_references(self, tool: Tool) -> None:
        tool.external_references.update(
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
