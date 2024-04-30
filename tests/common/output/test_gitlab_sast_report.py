from operator import itemgetter
from pathlib import Path

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.gitlab_sast import GitLabSast
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.sca.output import create_report_cve_record, _add_to_report_licenses_statuses
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


def test_iac_output():
    # given
    test_file = Path(__file__).parent / "fixtures/main.tf"
    report = Runner().run(
        root_folder="", files=[str(test_file)], runner_filter=RunnerFilter(checks=["CKV2_AWS_6", "CKV_AWS_18"])
    )

    # when
    gitlab_sast = GitLabSast(reports=[report])
    output = gitlab_sast.sast_json

    # then
    assert (
        output["schema"]
        == "https://gitlab.com/gitlab-org/security-products/security-report-schemas/-/raw/v15.0.4/dist/sast-report-format.json"
    )
    assert output["version"] == "15.0.4"

    # remove dynamic data
    del output["scan"]["start_time"]
    del output["scan"]["end_time"]
    del output["scan"]["analyzer"]["version"]
    assert output["scan"] == {
        "analyzer": {
            "id": "checkov",
            "name": "Checkov",
            "url": "https://www.checkov.io/",
            "vendor": {"name": "Bridgecrew"},
        },
        "scanner": {
            "id": "checkov",
            "name": "Checkov",
            "url": "https://www.checkov.io/",
            "vendor": {"name": "Bridgecrew"},
        },
        "status": "success",
        "type": "sast",
    }

    # remove dynamic data
    for vul in output["vulnerabilities"]:
        del vul["id"]
        del vul["solution"]
        del vul["description"]
        del vul["location"]["file"]
        if "links" in vul:
            del vul["links"]
            for ident in vul["identifiers"]:
                del ident["url"]
    assert sorted(output["vulnerabilities"], key=itemgetter("name")) == sorted(
        [
            {
                "identifiers": [{"name": "CKV2_AWS_6", "type": "checkov", "value": "CKV2_AWS_6"}],
                "location": {"start_line": 1, "end_line": 8},
                "name": "Ensure that S3 bucket has a Public Access block",
                "severity": "Unknown",
            },
            {
                "identifiers": [{"name": "CKV_AWS_18", "type": "checkov", "value": "CKV_AWS_18"}],
                "location": {"start_line": 1, "end_line": 8},
                "name": "Ensure the S3 bucket has access logging enabled",
                "severity": "Unknown",
            },
        ],
        key=itemgetter("name"),
    )


def test_sca_package_output():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package_2.scanner.Scanner"
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

    record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses="OSI_BDS",
        package={"package_registry": "https://registry.npmjs.org/", "is_private_registry": False},
    )
    # also add a BC_VUL_2 record
    bc_record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses="OSI_BDS",
        package={"package_registry": "https://registry.npmjs.org/", "is_private_registry": False},
    )
    bc_record.check_id = "BC_VUL_2"

    report = Report(CheckType.SCA_PACKAGE)
    report.add_resource(record.resource)
    report.add_record(record)
    report.add_record(bc_record)

    report.extra_resources.add(
        ExtraResource(
            file_abs_path=file_abs_path,
            file_path=f"/{rootless_file_path}",
            resource=f"{rootless_file_path}.testpkg",
            vulnerability_details={"package_name": "testpkg", "package_version": "1.1.1", "licenses": "MIT"},
        )
    )

    # when
    gitlab_sast = GitLabSast(reports=[report])
    output = gitlab_sast.sast_json

    # then

    # remove dynamic data
    for vul in output["vulnerabilities"]:
        del vul["id"]
    assert output["vulnerabilities"] == [
        {
            "identifiers": [
                {
                    "name": "CVE-2019-19844 - django: 1.2",
                    "type": "cve",
                    "url": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
                    "value": "CVE-2019-19844",
                }
            ],
            "links": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844"}],
            "location": {"file": "path/to/requirements.txt"},
            "name": "CVE-2019-19844 - django: 1.2",
            "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ...",
            "severity": "Medium",
            "solution": "fixed in 3.0.1, 2.2.9, 1.11.27",
        },
        {
            "identifiers": [
                {
                    "name": "CVE-2019-19844 - django: 1.2",
                    "type": "cve",
                    "url": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
                    "value": "CVE-2019-19844",
                }
            ],
            "links": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844"}],
            "location": {"file": "path/to/requirements.txt"},
            "name": "CVE-2019-19844 - django: 1.2",
            "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ...",
            "severity": "Medium",
            "solution": "fixed in 3.0.1, 2.2.9, 1.11.27",
        },
    ]


def test_sca_license_output():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package_2.scanner.Scanner"
    license_statuses = [
        {
            "package_name": "github.com/apparentlymart/go-textseg/v12",
            "package_version": "v12.0.0",
            "policy": "BC_LIC_1",
            "license": "Apache-2.0",
            "status": "COMPLIANT",
        },
        {
            "package_name": "docutils",
            "package_version": "0.15.2",
            "policy": "BC_LIC_1",
            "license": "GPL",
            "status": "OPEN",
        },
    ]
    sca_details = None

    report = Report(CheckType.SCA_PACKAGE)
    _add_to_report_licenses_statuses(
        report=report,
        check_class=check_class,
        scanned_file_path=file_abs_path,
        rootless_file_path=rootless_file_path,
        runner_filter=RunnerFilter(),
        packages_map=dict(),
        license_statuses=license_statuses,
        sca_details=sca_details,
        report_type=report.check_type,
    )

    # when
    gitlab_sast = GitLabSast(reports=[report])
    output = gitlab_sast.sast_json

    # then

    # remove dynamic data
    for vul in output["vulnerabilities"]:
        del vul["id"]
    assert output["vulnerabilities"] == [
        {
            "identifiers": [{"name": "BC_LIC_1", "type": "license", "value": "BC_LIC_1"}],
            "location": {"file": "path/to/requirements.txt"},
            "name": "License GPL - docutils: 0.15.2",
            "description": "Package docutils@0.15.2 has license GPL",
        }
    ]


def test_create_iac_vulnerability_with_non_url_guideline():
    # given
    # the report doesn't matter for this test, because we pass the record to method directly
    gitlab_sast = GitLabSast(reports=[])
    record = Record(
        check_id="CKV_AWS_5",
        check_name="Ensure all data stored in the Elasticsearch is securely encrypted at rest",
        check_result={"result": CheckResult.FAILED},
        code_block=[],
        file_path="./main.tf",
        file_line_range=[7, 10],
        resource="aws_elasticsearch_domain.enabled",
        evaluations=None,
        check_class="",
        file_abs_path=".",
        bc_check_id="BC_AWS_ELASTICSEARCH_3",
    )
    record.guideline = "Some guideline text"

    # when
    vulnerability = gitlab_sast._create_iac_vulnerability(record=record)

    # then
    # vulnerability["identifiers"][0]["url"] shouldn't exist
    assert vulnerability["identifiers"] == [{"name": "CKV_AWS_5", "type": "checkov", "value": "CKV_AWS_5"}]
    # vulnerability["links"] shouldn't exist
    assert "links" not in vulnerability
