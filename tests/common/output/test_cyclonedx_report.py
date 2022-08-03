import os
from pathlib import Path

from checkov.common.output.extra_resource import ExtraResource

from checkov.common.output.report import Report, CheckType
from cyclonedx.model.component import ComponentType
from pytest_mock import MockerFixture

from checkov.common.output.cyclonedx import CycloneDX
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

    assert len(next(iter(cyclonedx.bom.components)).get_vulnerabilities()) == 4

    assert "http://cyclonedx.org/schema/bom/1.4" in output


def test_sca_packages_cyclonedx_bom():
    from checkov.sca_package.output import create_report_cve_record
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
