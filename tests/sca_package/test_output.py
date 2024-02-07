from __future__ import annotations

from typing import Any

from packaging import version as packaging_version

from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.models.enums import CheckResult, ScanDataFormat
from checkov.common.sca.output import create_report_cve_record, create_report_license_record
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.output import (
    calculate_lowest_compliant_version,
    create_cli_cves_table,
    create_cli_license_violations_table,
    create_cli_output,
    CveCount,
)


def get_vulnerabilities_details() -> list[dict[str, Any]]:
    return [
        {
            "id": "CVE-2019-19844",
            "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
            "cvss": 9.8,
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ...",
            "severity": "critical",
            "packageName": "django",
            "packageVersion": "1.2",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
            "riskFactors": [
                "Attack complexity: low",
                "Attack vector: network",
                "Critical severity",
                "Has fix",
            ],
            "impactedVersions": ["<1.11.27"],
            "publishedDate": "2019-12-18T20:15:00+01:00",
            "discoveredDate": "2019-12-18T19:15:00Z",
            "fixDate": "2019-12-18T20:15:00+01:00",
        },
        {
            "id": "CVE-2016-6186",
            "status": "fixed in 1.9.8, 1.8.14",
            "cvss": 6.1,
            "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
            "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function ...",
            "severity": "medium",
            "packageName": "django",
            "packageVersion": "1.2",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
            "riskFactors": [
                "Attack complexity: low",
                "Attack vector: network",
                "Exploit exists",
                "Has fix",
                "Medium severity",
            ],
            "impactedVersions": ["<=1.8.13"],
            "publishedDate": "2016-08-05T17:59:00+02:00",
            "discoveredDate": "2016-08-05T15:59:00Z",
            "fixDate": "2016-08-05T17:59:00+02:00",
        },
    ]


def test_create_report_cve_record():
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
        "severity": "critical",
        "packageName": "django",
        "packageVersion": "1.12",
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
        package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
    )

    # then
    assert record.bc_check_id == "BC_CVE_2019_19844"
    assert record.check_id == "CKV_CVE_2019_19844"
    assert record.check_class == check_class
    assert record.check_name == "SCA package scan"
    assert record.check_result == {"result": CheckResult.FAILED}
    assert record.code_block == [(0, "django: 1.12")]
    assert (
        record.description
        == "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ..."
    )
    assert record.file_abs_path == file_abs_path
    assert record.file_line_range == [0, 0]
    assert record.file_path == f"/{rootless_file_path}"
    assert record.repo_file_path == file_abs_path
    assert record.resource == "requirements.txt.django"
    assert record.severity == Severities[BcSeverities.CRITICAL]
    assert record.short_description == "CVE-2019-19844 - django: 1.12"
    assert record.vulnerability_details["status"] == "fixed in 3.0.1, 2.2.9, 1.11.27"
    assert record.vulnerability_details["lowest_fixed_version"] == "2.2.9"
    assert record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("3.0.1"),
        packaging_version.parse("2.2.9"),
    ]
    assert record.vulnerability_details["licenses"] == 'OSI_BDS'


def test_create_report_cve_record_results_from_platform():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    vulnerability_details = {
                "severity": "CRITICAL",
                "riskFactors": "{\"Critical severity\":{},\"Attack vector: network\":{},\"Has fix\":{},\"Attack complexity: low\":{}}",
                "id": "CVE-2019-19844",
                "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
                "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)",
                "packageVersion": "1.2",
                "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "packageName": "django",
                "publishedDate": "2019-12-18T19:15:00Z",
                "cvss": 9.8,
                "status": "OPEN",
                "cveStatus": "1.11.27",
                "fileMetadataId": "d9f631f2-86b3-4d47-9b23-a2529c255392",
                "ViolationResource": {
                    "scannerType": "Twistcli",
                    "customerName": "ipeleg",
                    "status": "OPEN",
                    "firstDetectionDate": None,
                    "updatedDate": "2022-08-23T09:37:27.207Z",
                    "resourceId": "/packages/requirements.txt",
                    "violationId": "BC_VUL_2",
                    "sourceId": "itai1357/terragoat1",
                    "ticket": None,
                    "metadataFixId": None,
                    "originalResourceDefinition": None,
                    "fixedResourceDefinition": None,
                    "errorLine": None,
                    "resourcePlanId": None,
                    "errorLines": None,
                    "variableCode": None,
                    "variableFixCode": None,
                    "resourceFixCode": None,
                    "gitBlameMetadataId": None
                },
                "isRootPackage": None,
                "packageId": "49d27c4c-68cc-4eeb-ab98-d40a11334fdf",
                "causePackageId": "49d27c4c-68cc-4eeb-ab98-d40a11334fdf",
            }

    # when
    record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses='OSI_BDS',
        scan_data_format=ScanDataFormat.PLATFORM,
        package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
    )

    # then

    # in the case of scan_data_format=ScanDataFormat.FROM_PLATFORM we just have to make sure that 'status' and
    # 'fix_version' are as expected, as the rest are the same as in default flow
    # (can_data_format=ScanDataFormat.FROM_TWISTCLI)
    assert "lowest_fixed_version" not in record.vulnerability_details
    assert "fixed_versions" not in record.vulnerability_details
    assert record.vulnerability_details["fix_version"] == '1.11.27'


def test_create_report_cve_record_moderate_severity():
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
        package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
    )

    # then
    assert record.severity == Severities[BcSeverities.MEDIUM]


def test_create_report_cve_record_severity_filter():
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
        runner_filter=RunnerFilter(checks=['HIGH']),
        licenses='OSI_BDS',
        package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
    )

    # then
    assert record.bc_check_id == "BC_CVE_2019_19844"
    assert record.check_id == "CKV_CVE_2019_19844"
    assert record.check_class == check_class
    assert record.check_name == "SCA package scan"
    assert record.check_result == {"result": CheckResult.SKIPPED, 'suppress_comment': 'Filtered by severity'}
    assert record.code_block == [(0, "django: 1.2")]
    assert (
        record.description
        == "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ..."
    )
    assert record.file_abs_path == file_abs_path
    assert record.file_line_range == [0, 0]
    assert record.file_path == f"/{rootless_file_path}"
    assert record.repo_file_path == file_abs_path
    assert record.resource == "requirements.txt.django"
    assert record.severity == Severities[BcSeverities.MEDIUM]
    assert record.short_description == "CVE-2019-19844 - django: 1.2"
    assert record.vulnerability_details["lowest_fixed_version"] == "1.11.27"
    assert record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("3.0.1"),
        packaging_version.parse("2.2.9"),
        packaging_version.parse("1.11.27"),
    ]
    assert record.vulnerability_details["licenses"] == 'OSI_BDS'


def test_create_report_cve_record_package_filter():
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
        "severity": "critical",
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
        runner_filter=RunnerFilter(skip_cve_package=['django', 'requests']),
        licenses='OSI_BDS',
        package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
    )

    # then
    assert record.bc_check_id == "BC_CVE_2019_19844"
    assert record.check_id == "CKV_CVE_2019_19844"
    assert record.check_class == check_class
    assert record.check_name == "SCA package scan"
    assert record.check_result == {"result": CheckResult.SKIPPED, "suppress_comment": "Filtered by package 'django'"}
    assert record.code_block == [(0, "django: 1.2")]
    assert (
        record.description
        == "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ..."
    )
    assert record.file_abs_path == file_abs_path
    assert record.file_line_range == [0, 0]
    assert record.file_path == f"/{rootless_file_path}"
    assert record.repo_file_path == file_abs_path
    assert record.resource == "requirements.txt.django"
    assert record.severity == Severities[BcSeverities.CRITICAL]
    assert record.short_description == "CVE-2019-19844 - django: 1.2"
    assert record.vulnerability_details["lowest_fixed_version"] == "1.11.27"
    assert record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("3.0.1"),
        packaging_version.parse("2.2.9"),
        packaging_version.parse("1.11.27"),
    ]
    assert record.vulnerability_details["licenses"] == 'OSI_BDS'


def test_calculate_lowest_compliant_version():
    # given
    package_versions_list = [
        ["3.0.1", "2.2.9", "1.11.27", "1.9.8"],
        ["1.9.8", "1.8.14"],
        ["1.9.10", "1.8.15"],
        ["3.2.4", "3.1.12", "2.2.24"],
    ]

    fix_versions_lists = [
        [packaging_version.parse(version) for version in package_versions] for package_versions in package_versions_list
    ]

    # when
    compliant_version = calculate_lowest_compliant_version(fix_versions_lists)

    # then
    assert compliant_version == "2.2.24"


def test_create_cli_cves_table(mocker):
    mocker.patch("checkov.common.output.report.CHECKOV_RUN_SCA_PACKAGE_SCAN_V2", return_value=True)
    # given
    file_path = "/path/to/requirements.txt"
    cve_count = CveCount(total=6, critical=0, high=3, medium=2, low=0, skipped=1, has_fix=5, to_fix=5)
    package_details_map = {
        "django": {
            "cves": [
                {"id": "CVE-2016-7401", "severity": "high", "fixed_version": "1.8.15"},
                {"id": "CVE-2016-6186", "severity": "medium", "fixed_version": "1.8.14"},
                {"id": "CVE-2021-33203", "severity": "medium", "fixed_version": "2.2.24"},
            ],
            "current_version": "1.2",
            "compliant_version": "2.2.24",
        },
        "flask": {
            "cves": [
                {"id": "CVE-2019-1010083", "severity": "high", "fixed_version": "1.0"},
                {"id": "CVE-2018-1000656", "severity": "high", "fixed_version": "0.12.3"},
            ],
            "current_version": "0.6",
            "compliant_version": "1.0",
        },
    }

    # when
    table = create_cli_cves_table(
        file_path=file_path,
        cve_count=cve_count,
        package_details_map=package_details_map,
    )

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt - CVEs Summary:\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVEs: 6      │ critical: 0        │ high: 3            │ medium: 2          │ low: 0             │ skipped: 1         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 5/5 CVEs, go to your Prisma Cloud account                                                                            │\n",
            "\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤\n",
            "\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │\n",
            "\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n",
            "\t│ django             │ CVE-2016-7401      │ high               │ 1.2                │ 1.8.15             │ 2.2.24             │\n",
            "\t│                    │ CVE-2016-6186      │ medium             │                    │ 1.8.14             │                    │\n",
            "\t│                    │ CVE-2021-33203     │ medium             │                    │ 2.2.24             │                    │\n",
            "\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n",
            "\t│ flask              │ CVE-2019-1010083   │ high               │ 0.6                │ 1.0                │ 1.0                │\n",
            "\t│                    │ CVE-2018-1000656   │ high               │                    │ 0.12.3             │                    │\n",
            "\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘\n",
        ]
    )


def test_create_cli_license_violations_table(mocker):
    mocker.patch("checkov.common.output.report.CHECKOV_RUN_SCA_PACKAGE_SCAN_V2", return_value=True)

    # given
    file_path = "/requirements.txt"

    package_licenses_details_map = {
        "django": [
            {
                "package_name": "django",
                "package_version": "1.2",
                "license": "DUMMY_LICENSE",
                "status": "OPEN",
                "policy": "BC_LIC_1"
            },
            {
                "package_name": "django",
                "package_version": "1.2",
                "license": "DUMMY_LICENSE2",
                "status": "OPEN",
                "policy": "BC_LIC_1"
            },
        ],
        "flask": [
            {
                "package_name": "flask",
                "package_version": "0.6",
                "license": "DUMMY_LICENSE3",
                "status": "OPEN",
                "policy": "BC_LIC_1"
            },
        ]
    }

    # when
    table = create_cli_license_violations_table(
        file_path=file_path,
        package_licenses_details_map=package_licenses_details_map
    )

    # then
    assert table == "".join(
        [
            "\t/requirements.txt - Licenses Statuses:\n",
            "\t┌────────────────────────┬────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┐\n",
            "\t│ Package name           │ Package version        │ Policy ID              │ License                │ Status                  │\n",
            "\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤\n",
            "\t│ django                 │ 1.2                    │ BC_LIC_1               │ DUMMY_LICENSE          │ OPEN                    │\n",
            "\t│                        │                        │ BC_LIC_1               │ DUMMY_LICENSE2         │ OPEN                    │\n",
            "\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤\n",
            "\t│ flask                  │ 0.6                    │ BC_LIC_1               │ DUMMY_LICENSE3         │ OPEN                    │\n",
            "\t└────────────────────────┴────────────────────────┴────────────────────────┴────────────────────────┴─────────────────────────┘\n",
        ]
    )


def test_create_cli_cves_table_with_no_found_vulnerabilities(mocker):
    mocker.patch("checkov.common.output.report.CHECKOV_RUN_SCA_PACKAGE_SCAN_V2", return_value=True)

    # given
    file_path = "/path/to/requirements.txt"
    cve_count = CveCount(total=2, critical=0, high=0, medium=0, low=0, skipped=2, has_fix=0, to_fix=0)
    package_details_map = {}

    # when
    table = create_cli_cves_table(
        file_path=file_path,
        cve_count=cve_count,
        package_details_map=package_details_map,
    )

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt - CVEs Summary:\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVEs: 2      │ critical: 0        │ high: 0            │ medium: 0          │ low: 0             │ skipped: 2         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 0/0 CVEs, go to your Prisma Cloud account                                                                            │\n",
            "\t└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘\n",
        ]
    )


def test_create_cli_output(mocker):
    mocker.patch("checkov.common.output.report.CHECKOV_RUN_SCA_PACKAGE_SCAN_V2", return_value=True)
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    license_statuses = [
        {
            "package_name": "django",
            "package_version": "1.2",
            "license": "DUMMY_LICENSE",
            "status": "OPEN",
            "policy": "BC_LIC_1"
        },
        {
            "package_name": "flask",
            "package_version": "0.6",
            "license": "DUMMY_OTHER_LICENSE",  # not a real license. it is just for test a package with 2 licenses
            "status": "OPEN",
            "policy": "BC_LIC_1"
        }
    ]
    # when
    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details,
            licenses='Unknown',
            package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
        )
        for details in get_vulnerabilities_details()
    ]
    license_records = [
            create_report_license_record(
                rootless_file_path=rootless_file_path,
                file_abs_path=file_abs_path,
                check_class=check_class,
                licenses_status=license_status,
                package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
            )
            for license_status in license_statuses
        ]
    cli_output = create_cli_output(True, cves_records + license_records)

    # then
    assert cli_output == "".join(
        [
            "\t/requirements.txt - CVEs Summary:\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVEs: 2      │ critical: 1        │ high: 0            │ medium: 1          │ low: 0             │ skipped: 0         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 2/2 CVEs, go to your Prisma Cloud account                                                                            │\n",
            "\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤\n",
            "\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │\n",
            "\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n",
            "\t│ django             │ CVE-2019-19844     │ critical           │ 1.2                │ 1.11.27            │ 1.11.27            │\n",
            "\t│                    │ CVE-2016-6186      │ medium             │                    │ 1.8.14             │                    │\n",
            "\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘\n",
            "\n",
            "\t/requirements.txt - Licenses Statuses:\n",
            "\t┌────────────────────────┬────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┐\n",
            "\t│ Package name           │ Package version        │ Policy ID              │ License                │ Status                  │\n",
            "\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤\n",
            "\t│ django                 │ 1.2                    │ BC_LIC_1               │ DUMMY_LICENSE          │ FAILED                  │\n",
            "\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤\n",
            "\t│ flask                  │ 0.6                    │ BC_LIC_1               │ DUMMY_OTHER_LICENSE    │ FAILED                  │\n",
            "\t└────────────────────────┴────────────────────────┴────────────────────────┴────────────────────────┴─────────────────────────┘\n",
        ]
    )


def test_create_cli_output_without_license_records(mocker):
    mocker.patch("checkov.common.output.report.CHECKOV_RUN_SCA_PACKAGE_SCAN_V2", return_value=True)
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    # when
    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details,
            licenses='Unknown',
            package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
        )
        for details in get_vulnerabilities_details()
    ]
    cli_output = create_cli_output(True, cves_records)

    # then
    assert cli_output == "".join(
        [
            "\t/requirements.txt - CVEs Summary:\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVEs: 2      │ critical: 1        │ high: 0            │ medium: 1          │ low: 0             │ skipped: 0         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 2/2 CVEs, go to your Prisma Cloud account                                                                            │\n",
            "\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤\n",
            "\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │\n",
            "\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n",
            "\t│ django             │ CVE-2019-19844     │ critical           │ 1.2                │ 1.11.27            │ 1.11.27            │\n",
            "\t│                    │ CVE-2016-6186      │ medium             │                    │ 1.8.14             │                    │\n",
            "\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘\n",
        ]
    )


def test_create_cli_output_without_cve_records(mocker):
    mocker.patch("checkov.common.output.report.CHECKOV_RUN_SCA_PACKAGE_SCAN_V2", return_value=True)
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    license_statuses = [
        {
            "package_name": "django",
            "package_version": "1.2",
            "license": "DUMMY_LICENSE",
            "status": "OPEN",
            "policy": "BC_LIC_1"
        },
        {
            "package_name": "flask",
            "package_version": "0.6",
            "license": "DUMMY_OTHER_LICENSE",  # not a real license. it is just for test a package with 2 licenses
            "status": "OPEN",
            "policy": "BC_LIC_1"
        }
    ]
    # when
    license_records = [
            create_report_license_record(
                rootless_file_path=rootless_file_path,
                file_abs_path=file_abs_path,
                check_class=check_class,
                licenses_status=license_status,
                package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
            )
            for license_status in license_statuses
        ]
    cli_output = create_cli_output(True, license_records)

    # then
    assert cli_output == "".join(
        [
            "\t/requirements.txt - Licenses Statuses:\n",
            "\t┌────────────────────────┬────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┐\n",
            "\t│ Package name           │ Package version        │ Policy ID              │ License                │ Status                  │\n",
            "\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤\n",
            "\t│ django                 │ 1.2                    │ BC_LIC_1               │ DUMMY_LICENSE          │ FAILED                  │\n",
            "\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤\n",
            "\t│ flask                  │ 0.6                    │ BC_LIC_1               │ DUMMY_OTHER_LICENSE    │ FAILED                  │\n",
            "\t└────────────────────────┴────────────────────────┴────────────────────────┴────────────────────────┴─────────────────────────┘\n",
        ]
    )
