import json
import os
from pathlib import Path

from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.vulnerability import VulnerabilitySeverity
from packageurl import PackageURL
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.report import Report, CheckType
from pytest_mock import MockerFixture

from checkov.common.output.common import ImageDetails
from checkov.common.output.cyclonedx import CycloneDX
from checkov.common.sca.output import create_report_cve_record
from checkov.common.output.record import Record
from checkov.terraform.runner import Runner


def test_valid_cyclonedx_bom():
    # given
    test_file = Path(__file__).parent / "fixtures/main.tf"
    repo_id = "acme/example"
    report = Runner().run(root_folder="", files=[str(test_file)])

    # when
    cyclonedx = CycloneDX(repo_id=repo_id, reports=[report])
    output = cyclonedx.get_xml_output()

    # then
    assert len(cyclonedx.bom.components) == 1

    component = next(iter(cyclonedx.bom.components))

    assert component.name == 'aws_s3_bucket.destination'
    assert component.purl.name == 'aws_s3_bucket.destination'
    assert component.purl.namespace == 'acme/example/main.tf'
    assert component.purl.type == 'terraform'
    assert component.purl.version.startswith('sha1:')
    assert component.type == ComponentType.APPLICATION

    vulnerabilities = next(iter(cyclonedx.bom.components)).get_vulnerabilities()
    assert len(vulnerabilities) == 4
    # doesn't matter which vulnerability, they are all unknown for runs without platform connection
    assert next(iter(next(iter(vulnerabilities)).ratings)).severity == VulnerabilitySeverity.UNKNOWN

    assert "http://cyclonedx.org/schema/bom/1.4" in output

def test_valid_cyclonedx_image_bom():
    # given
    repo_id = 'acme/repo'
    rootless_file_path = "Dockerfile (sha256:123456)"
    file_abs_path = "/path/to/Dockerfile (sha256:123456)"
    check_class = "checkov.common.bridgecrew.vulnerability_scanning.sca_scanner.imageScanner"
    image_details: ImageDetails = ImageDetails(
        distro='Debian GNU/Linux 11 (bullseye)',
        distro_release='bullseye',
        package_types={'curl@7.74.0-1.3+deb11u1': 'os'},
        image_id='ubuntu:latest'
    )
    vulnerability = {
        'id': 'CVE-2022-32207',
        'status': 'fixed in 7.74.0-1.3+deb11u2',
        'cvss': 9.8,
        'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
        'description': 'When curl < 7.84.0 saves cookies, alt-svc and hsts data to local files, it makes the operation atomic by finalizing the operation with a rename from a temporary name to the final target file name.In that rename operation, it might accidentally *widen* the permissions for the target file, leaving the updated file accessible to more users than intended.',
        'severity': 'critical',
        'packageName': 'curl',
        'packageVersion': '7.74.0-1.3+deb11u1',
        'link': 'https://security-tracker.debian.org/tracker/CVE-2022-32207',
        'riskFactors': [
            'Attack complexity: low',
            'Attack vector: network',
            'Critical severity',
            'Has fix',
            'Recent vulnerability'
        ],
        'impactedVersions': ['<7.74.0-1.3+deb11u2'],
        'publishedDate': '2022-07-07T16:15:00+03:00',
        'discoveredDate': '2022-08-02T14:05:40+03:00',
        'fixDate': '2022-07-07T16:15:00+03:00'
    }

    record: Record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability,
        licenses="BSD-3-Clause",
        sca_details=image_details,
    )
    report = Report(check_type='sca_image')
    report.add_record(record)

    # when
    cyclonedx = CycloneDX(repo_id=repo_id, reports=[report])
    output = cyclonedx.get_xml_output()

    # then
    assert len(cyclonedx.bom.components) == 2
    package_purl = PackageURL(
        name='curl',
        namespace='acme/repo/Dockerfile/debian',
        type='deb',
        version='7.74.0-1.3+deb11u1',
        qualifiers={'distro': 'bullseye'}
    )

    package_component = cyclonedx.bom.get_component_by_purl(purl=package_purl)

    assert package_component is not None
    assert package_component.name == "curl"
    assert package_component.type == ComponentType.LIBRARY
    assert package_component.version == "7.74.0-1.3+deb11u1"
    assert len(package_component.licenses) == 1
    assert next(iter(package_component.licenses)).license.name == "BSD-3-Clause"

    vulnerabilities = package_component.get_vulnerabilities()
    assert len(vulnerabilities) == 1
    assert next(iter(next(iter(vulnerabilities)).ratings)).severity == VulnerabilitySeverity.CRITICAL

    image_purl = PackageURL(
        name='Dockerfile',
        namespace='acme/repo',
        type='oci',
        version='ubuntu:latest',
    )
    image_component = Component(
        name='acme/repo//ubuntu:latest',
        purl=image_purl,
        group=None,
        component_type=ComponentType.CONTAINER,
        version=''
    )
    assert cyclonedx.bom.has_component(image_component)

    assert "http://cyclonedx.org/schema/bom/1.4" in output


def test_sca_packages_cyclonedx_bom():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    vulnerability_details = {
        "id": "CVE-2019-19844",
        "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
        "cvss": 9.8,
        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ...",
        "severity": "moderate",
        "packageName": "django",
        "packageVersion": "1.2",
        "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
        "riskFactors": ["Attack complexity: low", "Attack vector: network", "Critical severity", "Has fix"],
        "impactedVersions": ["<1.11.27"],
        "publishedDate": "2019-12-18T20:15:00+01:00",
        "discoveredDate": "2019-12-18T19:15:00Z",
        "fixDate": "2019-12-18T20:15:00+01:00",
    }

    # when
    record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses='OSI_BDS',
    )

    report = Report(CheckType.SCA_PACKAGE)
    report.add_resource(record.resource)
    report.add_record(record)

    report.extra_resources.add(
        ExtraResource(
            file_abs_path=file_abs_path,
            file_path=f"/{rootless_file_path}",
            resource=f'{rootless_file_path}.testpkg',
            vulnerability_details={
                "package_name": "testpkg",
                "package_version": "1.1.1",
                "licenses": "MIT"
            }
        )
    )

    cyclonedx = CycloneDX([report], "repoid/test")
    output = cyclonedx.get_xml_output()

    # then
    assert output

def test_create_schema_version_1_3(mocker: MockerFixture):
    # given
    test_file = Path(__file__).parent / "fixtures/main.tf"
    repo_id = "acme/example"
    report = Runner().run(root_folder="", files=[str(test_file)])

    mocker.patch.dict(os.environ, {"CHECKOV_CYCLONEDX_SCHEMA_VERSION": "1.3"})

    # when
    cyclonedx = CycloneDX(repo_id=repo_id, reports=[report])
    output = cyclonedx.get_xml_output()

    # then
    assert len(cyclonedx.bom.components) == 1
    assert len(next(iter(cyclonedx.bom.components)).get_vulnerabilities()) == 4

    assert "http://cyclonedx.org/schema/bom/1.3" in output


def test_create_library_component_maven_package() -> None:
    # given
    cyclone = CycloneDX([Report(CheckType.SCA_IMAGE)], repo_id="12345")
    package = {"name": 'org.bouncycastle_bcpkix-jdk15on',
               "version": '1.69.00'}
    rootless_file_path = "Dockerfile"

    resource = ExtraResource(
        file_abs_path="/path/to/Dockerfile",
        file_path=rootless_file_path,
        resource=f"{rootless_file_path}.{package['name']}",
        vulnerability_details={
            "package_name": package["name"],
            "package_version": package["version"],
            "licenses": "Unknown",
            "package_type": 'jar',
        },
    )

    component = cyclone.create_library_component(resource, CheckType.SCA_IMAGE)

    assert component.purl.name == 'bcpkix-jdk15on'
    assert component.purl.version == '1.69.00'
    assert component.purl.namespace == '12345/Dockerfile/org.bouncycastle'


def test_create_library_component_maven_package_without_group_name() -> None:
    # given
    cyclone = CycloneDX([Report(CheckType.SCA_IMAGE)], repo_id="12345")
    package = {"name": 'bcpkix-jdk15on',
               "version": '1.69.00'}
    rootless_file_path = "Dockerfile"

    resource = ExtraResource(
        file_abs_path="/path/to/Dockerfile",
        file_path=rootless_file_path,
        resource=f"{rootless_file_path}.{package['name']}",
        vulnerability_details={
            "package_name": package["name"],
            "package_version": package["version"],
            "licenses": "Unknown",
            "package_type": 'jar',
        },
    )

    component = cyclone.create_library_component(resource, CheckType.SCA_IMAGE)

    assert component.purl.name == 'bcpkix-jdk15on'
    assert component.purl.version == '1.69.00'
    assert component.purl.namespace == '12345/Dockerfile'


def test_create_json_output():
    # given
    test_file = Path(__file__).parent / "fixtures/main.tf"
    repo_id = "acme/example"
    report = Runner().run(root_folder="", files=[str(test_file)])

    # when
    cyclonedx = CycloneDX(repo_id=repo_id, reports=[report])
    output = json.loads(cyclonedx.get_json_output())

    # then
    assert output["$schema"] == "http://cyclonedx.org/schema/bom-1.4.schema.json"
    assert len(output["components"]) == 1
    assert len(output["dependencies"]) == 1
    assert len(output["vulnerabilities"]) == 4
