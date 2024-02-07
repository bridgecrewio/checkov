from __future__ import annotations

import os
from packaging import version as packaging_version
from pathlib import Path

from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.models.enums import CheckResult, ScanDataFormat
from checkov.common.sca.output import create_report_cve_record, create_report_license_record
from checkov.runner_filter import RunnerFilter
from checkov.sca_package_2.output import (
    calculate_lowest_compliant_version,
    create_cli_cves_table,
    create_cli_output,
    CveCount,
)
from tests.sca_package_2.conftest import get_vulnerabilities_details_package_json, get_vulnerabilities_details, \
    get_vulnerabilities_details_no_deps, get_vulnerabilities_details_package_lock_json, \
    create_cli_license_violations_table_wrapper, create_cli_output_wrapper, get_vulnerabilities_details_is_used_packages

CLI_OUTPUTS_DIR = Path(__file__).parent / "outputs" / "cli_outputs"


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
        "fixCode": "django==2.2.9",
        "fixCommand": {"msg": "After updating package version manually, run:",
                       "cmds": ["pip install -r requirements.txt"], "manualCodeFix": True}
    }

    # when
    record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses='OSI_BDS',
        package={'name': "django", 'version': "1.12", 'package_registry': "https://registry.npmjs.org/",
                 'is_private_registry': False, "lines": [5, 5], "code_block": 'django==1.12'},
        root_package={'name': "django", 'version': "1.12", "lines": [5, 5]},
        used_private_registry=False
    )

    # then
    assert record.bc_check_id == "BC_CVE_2019_19844"
    assert record.check_id == "CKV_CVE_2019_19844"
    assert record.check_class == check_class
    assert record.check_name == "SCA package scan"
    assert record.check_result == {"result": CheckResult.FAILED}
    assert record.code_block == [(5, 'django==1.12')]
    assert (
            record.description
            == "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ..."
    )
    assert record.file_abs_path == file_abs_path
    assert record.file_line_range == [5, 5]
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
    assert record.vulnerability_details["root_package_version"] == "1.12"
    assert record.vulnerability_details["root_package_name"] == "django"
    assert record.fixed_definition == 'django==2.2.9'
    assert record.vulnerability_details["fix_command"] == {'msg': 'After updating package version manually, run:',
                                                           'cmds': ['pip install -r requirements.txt'],
                                                           'manualCodeFix': True}


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
        "root_package_alias": 'django@1.2',
        "root_package_version": "1.2",
        "root_package_name": 'django'
    }

    # when
    record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses='OSI_BDS',
        package={'name': "django", 'version': "1.12", 'package_registry': "https://registry.npmjs.org/",
                 'is_private_registry': False, "lines": [6, 6], "code_block": 'django==1.12'},
        scan_data_format=ScanDataFormat.PLATFORM,
        root_package={'name': "django", 'version': "1.2"},
        used_private_registry=False
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
        "root_package_alias": 'django@1.2',
        "root_package_version": '1.2',
        "root_package_name": 'django'
    }

    # when
    record = create_report_cve_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        licenses='OSI_BDS',
        package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
        root_package={'name': "django", 'version': "1.2"},
        used_private_registry=False
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
        "root_package_alias": 'django@1.2',
        "root_package_version": '1.2',
        "root_package_name": 'django'
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
        root_package={'name': "django", 'version': "1.2"},
        used_private_registry=False
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
        "root_package_alias": 'django@1.2',
        "root_package_version": '1.2',
        "root_package_name": 'django',
        "fixCode": 'django==1.11.27',
        "fixCommand": {"msg": "After updating package version manually, run:",
                       "cmds": ["pip install -r requirements.txt"], "manualCodeFix": True}
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
        root_package={'name': "django", 'version': "1.2"},
        used_private_registry=False
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


def test_create_cli_cves_table():
    # given
    file_path = "/path/to/requirements.txt"
    cve_count = CveCount(total=6, critical=0, high=3, medium=2, low=0, skipped=1, has_fix=5, to_fix=5)
    package_details_map = {
        'django@1.2': {
            'cves': [{'id': 'CVE-2016-7401', 'severity': 'high', 'fixed_version': '1.8.15',
                      "root_package_name": 'django',
                      "root_package_version:": "1.2",
                      "package_name": 'django',
                      "package_version": "1.2",
                      "is_private_fix": None,
                      "lines": [1, 2]},
                     {'id': 'CVE-2016-6186', 'severity': 'medium', 'fixed_version': '1.8.14',
                      "root_package_name": 'django',
                      "root_package_version:": "1.2",
                      "package_name": 'django',
                      "package_version": "1.2",
                      "is_private_fix": None
                      },
                     {'id': 'CVE-2021-33203', 'severity': 'medium', 'fixed_version': '2.2.24',
                      "root_package_name": 'django',
                      "root_package_version:": "1.2",
                      "package_name": 'django',
                      "package_version": "1.2",
                      "is_private_fix": None
                      }],
            'compliant_version': '2.2.24'},
        'flask@0.6': {
            'cves': [{'id': 'CVE-2019-1010083', 'severity': 'high', 'fixed_version': '1.0',
                      "root_package_name": 'flask',
                      "root_package_version:": "0.6",
                      "package_name": 'flask',
                      "package_version": "0.6",
                      "is_private_fix": None
                      },
                     {'id': 'CVE-2018-1000656', 'severity': 'high', 'fixed_version': '0.12.3',
                      "root_package_name": 'flask',
                      "root_package_version:": "0.6",
                      "package_name": 'flask',
                      "package_version": "0.6",
                      "is_private_fix": None
                      }],
            'compliant_version': '1.0'}}

    # when
    table = create_cli_cves_table(
        file_path=file_path,
        cve_count=cve_count,
        package_details_map=package_details_map,
        lines_details_found=True
    )

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt - CVEs Summary:\n",
            "\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n",
            "\t│ Total CVEs: 6        │ critical: 0          │ high: 3              │ medium: 2            │ low: 0               │ skipped: 1           │ Total Packages Used: │\n",
            "\t│                      │                      │                      │                      │                      │                      │ 0                    │\n",
            "\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n",
            "\t│ To fix 5/5 CVEs, go to your Prisma Cloud account                                                                                                               │\n",
            "\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n",
            "\t│ Package [Lines]      │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
            "\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n",
            "\t│ django [1-2]         │ CVE-2016-7401        │ high                 │ 1.2                  │ 1.8.15               │ 2.2.24               │                      │\n",
            "\t│                      │ CVE-2016-6186        │ medium               │                      │ 1.8.14               │                      │                      │\n",
            "\t│                      │ CVE-2021-33203       │ medium               │                      │ 2.2.24               │                      │                      │\n",
            "\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n",
            "\t│ flask                │ CVE-2019-1010083     │ high                 │ 0.6                  │ 1.0                  │ 1.0                  │                      │\n",
            "\t│                      │ CVE-2018-1000656     │ high                 │                      │ 0.12.3               │                      │                      │\n",
            "\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n",
        ]
    )


def test_create_cli_license_violations_table_no_line_numbers():
    # when
    table = create_cli_license_violations_table_wrapper(with_line_numbers=False)

    # then
    assert table == "".join(
        [
            "\t/requirements.txt - Licenses Statuses:\n",
            "\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────┐\n",
            "\t│ Package name             │ Package version          │ Policy ID                │ License                  │ Status                    │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ django                   │ 1.2                      │ BC_LIC_1                 │ DUMMY_LICENSE            │ OPEN                      │\n",
            "\t│                          │                          │ BC_LIC_1                 │ DUMMY_LICENSE2           │ OPEN                      │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ django                   │ 1.12                     │ BC_LIC_1                 │ DUMMY_LICENSE3           │ OPEN                      │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ flask                    │ 0.6                      │ BC_LIC_1                 │ DUMMY_LICENSE3           │ OPEN                      │\n",
            "\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┘\n",
        ]
    )


def test_create_cli_license_violations_table_with_line_numbers():
    # when
    table = create_cli_license_violations_table_wrapper(with_line_numbers=True)

    # then
    assert table == "".join(
        [
            "\t/requirements.txt - Licenses Statuses:\n",
            "\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────┐\n",
            "\t│ Package name [Lines]     │ Package version          │ Policy ID                │ License                  │ Status                    │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ django [1-2]             │ 1.2                      │ BC_LIC_1                 │ DUMMY_LICENSE            │ OPEN                      │\n",
            "\t│                          │                          │ BC_LIC_1                 │ DUMMY_LICENSE2           │ OPEN                      │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ django                   │ 1.12                     │ BC_LIC_1                 │ DUMMY_LICENSE3           │ OPEN                      │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ flask [5-6]              │ 0.6                      │ BC_LIC_1                 │ DUMMY_LICENSE3           │ OPEN                      │\n",
            "\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┘\n",
        ]
    )


def test_create_cli_cves_table_with_no_found_vulnerabilities():
    # given
    file_path = "/path/to/requirements.txt"
    cve_count = CveCount(total=2, critical=0, high=0, medium=0, low=0, skipped=2, has_fix=0, to_fix=0)
    package_details_map = {}

    # when
    table = create_cli_cves_table(
        file_path=file_path,
        cve_count=cve_count,
        package_details_map=package_details_map,
        lines_details_found=False
    )

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt - CVEs Summary:\n",
            "\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n",
            "\t│ Total CVEs: 2        │ critical: 0          │ high: 0              │ medium: 0            │ low: 0               │ skipped: 2           │ Total Packages Used: │\n",
            "\t│                      │                      │                      │                      │                      │                      │ 0                    │\n",
            "\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n",
            "\t│ To fix 0/0 CVEs, go to your Prisma Cloud account                                                                                                               │\n",
            "\t└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘\n",
        ]
    )


def test_create_cli_output_no_line_numbers():
    # when
    cli_output = create_cli_output_wrapper(with_line_numbers=False)

    # then
    assert cli_output == "".join(
        [
            "\t/requirements.txt - CVEs Summary:\n",
            "\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n"
            "\t│ Total CVEs: 2        │ critical: 1          │ high: 0              │ medium: 1            │ low: 0               │ skipped: 0           │ Total Packages Used: │\n"
            "\t│                      │                      │                      │                      │                      │                      │ 0                    │\n"
            "\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n"
            "\t│ To fix 2/2 CVEs, go to your Prisma Cloud account                                                                                                               │\n"
            "\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n"
            "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n"
            "\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n"
            "\t│ django               │ CVE-2019-19844       │ CRITICAL             │ 1.2                  │ 1.11.27              │ 1.11.27              │                      │\n"
            "\t│                      │ CVE-2016-6186        │ MEDIUM               │                      │ 1.8.14               │                      │                      │\n"
            "\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n"
            "\n",
            "\t/requirements.txt - Licenses Statuses:\n",
            "\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────┐\n"
            "\t│ Package name             │ Package version          │ Policy ID                │ License                  │ Status                    │\n"
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n"
            "\t│ django                   │ 1.2                      │ BC_LIC_1                 │ DUMMY_LICENSE            │ FAILED                    │\n"
            "\t│                          │                          │ BC_LIC_1                 │ DUMMY_LICENSE2           │ FAILED                    │\n"
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n"
            "\t│ django                   │ 1.12                     │ BC_LIC_2                 │ DUMMY_LICENSE_3          │ FAILED                    │\n"
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n"
            "\t│ flask                    │ 0.6                      │ BC_LIC_1                 │ DUMMY_OTHER_LICENSE      │ FAILED                    │\n"
            "\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┘\n"
        ]
    )


def test_create_cli_output_with_line_numbers():
    # when
    cli_output = create_cli_output_wrapper(with_line_numbers=True)

    # then
    assert cli_output == "".join(
        [
            "\t/requirements.txt - CVEs Summary:\n",
            "\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n"
            "\t│ Total CVEs: 2        │ critical: 1          │ high: 0              │ medium: 1            │ low: 0               │ skipped: 0           │ Total Packages Used: │\n"
            "\t│                      │                      │                      │                      │                      │                      │ 0                    │\n"
            "\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n"
            "\t│ To fix 2/2 CVEs, go to your Prisma Cloud account                                                                                                               │\n"
            "\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n"
            "\t│ Package [Lines]      │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n"
            "\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n"
            "\t│ django [1-2]         │ CVE-2019-19844       │ CRITICAL             │ 1.2                  │ 1.11.27              │ 1.11.27              │                      │\n"
            "\t│                      │ CVE-2016-6186        │ MEDIUM               │                      │ 1.8.14               │                      │                      │\n"
            "\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n"
            "\n",
            "\t/requirements.txt - Licenses Statuses:\n",
            "\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────┐\n"
            "\t│ Package name [Lines]     │ Package version          │ Policy ID                │ License                  │ Status                    │\n"
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n"
            "\t│ django [1-2]             │ 1.2                      │ BC_LIC_1                 │ DUMMY_LICENSE            │ FAILED                    │\n"
            "\t│                          │                          │ BC_LIC_1                 │ DUMMY_LICENSE2           │ FAILED                    │\n"
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n"
            "\t│ django                   │ 1.12                     │ BC_LIC_2                 │ DUMMY_LICENSE_3          │ FAILED                    │\n"
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n"
            "\t│ flask [5-6]              │ 0.6                      │ BC_LIC_1                 │ DUMMY_OTHER_LICENSE      │ FAILED                    │\n"
            "\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┘\n"
        ]
    )


def test_create_cli_output_without_license_records():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package_2.scanner.Scanner"
    # when
    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details,
            licenses='Unknown',
            package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
            root_package={'name': "django", 'version': "1.2"},
            used_private_registry=False
        )
        for details in get_vulnerabilities_details()
    ]
    cli_output = create_cli_output(True, cves_records)
    # then
    assert cli_output == "".join(
        [
            "\t/requirements.txt - CVEs Summary:\n",
            "\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n",
            "\t│ Total CVEs: 2        │ critical: 1          │ high: 0              │ medium: 1            │ low: 0               │ skipped: 0           │ Total Packages Used: │\n"
            "\t│                      │                      │                      │                      │                      │                      │ 0                    │\n"
            "\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n"
            "\t│ To fix 2/2 CVEs, go to your Prisma Cloud account                                                                                                               │\n"
            "\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n"
            "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n"
            "\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n"
            "\t│ django               │ CVE-2019-19844       │ CRITICAL             │ 1.2                  │ 1.11.27              │ 1.11.27              │                      │\n"
            "\t│                      │ CVE-2016-6186        │ MEDIUM               │                      │ 1.8.14               │                      │                      │\n"
            "\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n"
        ]
    )


def test_create_cli_output_without_cve_records():
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
            "\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────┐\n",
            "\t│ Package name             │ Package version          │ Policy ID                │ License                  │ Status                    │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ django                   │ 1.2                      │ BC_LIC_1                 │ DUMMY_LICENSE            │ FAILED                    │\n",
            "\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n",
            "\t│ flask                    │ 0.6                      │ BC_LIC_1                 │ DUMMY_OTHER_LICENSE      │ FAILED                    │\n",
            "\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┘\n",
        ]
    )


def test_create_cli_table_for_sca_package_with_dependencies():
    # given
    rootless_file_path = "package-lock.json"
    file_abs_path = "/path/to/package-lock.json"
    check_class = "checkov.sca_package_2.scanner.Scanner"
    # when

    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details["details"],
            licenses='Unknown',
            package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
            root_package={'name': details["root_package_name"], 'version': details["root_package_version"]},
            used_private_registry=False,
            root_package_cve={'fixVersion': details.get('root_package_fix_version')}
        )
        for details in get_vulnerabilities_details_package_json()
    ]

    cli_output = create_cli_output(True, cves_records)
    # then
    assert cli_output == "".join([
        "\t/package-lock.json - CVEs Summary:\n",
        '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
        '\t│ Total CVEs: 26       │ critical: 4          │ high: 10             │ medium: 11           │ low: 1               │ skipped: 0           │ Total Packages Used: │\n',
        '\t│                      │                      │                      │                      │                      │                      │ 0                    │\n',
        '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
        '\t│ To fix 24/26 CVEs, go to your Prisma Cloud account                                                                                                             │\n',
        '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
        "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ cypress              │ PRISMA-2021-0070     │ MEDIUM               │ 3.8.3                │ 7.2.0                │ 7.2.0                │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ forever              │                      │                      │ 2.0.0                │                      │ N/A                  │                      │\n',
        '\t│ ├─ decode-uri-       │ CVE-2022-38900       │ LOW                  │ 0.2.0                │                      │                      │                      │\n',
        '\t│ component            │                      │                      │                      │                      │                      │                      │\n',
        '\t│ ├─ glob-parent       │ CVE-2020-28469       │ HIGH                 │ 3.1.0                │                      │                      │                      │\n',
        '\t│ ├─ minimist          │ CVE-2021-44906       │ CRITICAL             │ 0.0.10               │                      │                      │                      │\n',
        '\t│ │                    │ CVE-2020-7598        │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t│ ├─ minimist          │ CVE-2021-44906       │ CRITICAL             │ 1.2.5                │                      │                      │                      │\n',
        '\t│ ├─ nconf             │ CVE-2022-21803       │ HIGH                 │ 0.10.0               │                      │                      │                      │\n',
        '\t│ ├─ nconf             │ CVE-2022-21803       │ HIGH                 │ 0.6.9                │                      │                      │                      │\n',
        '\t│ └─ unset-value       │ PRISMA-2022-0049     │ HIGH                 │ 1.0.0                │                      │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ grunt                │ CVE-2022-1537        │ HIGH                 │ 1.4.1                │ 1.5.3                │ 1.5.3                │                      │\n',
        '\t│                      │ CVE-2022-0436        │ MEDIUM               │                      │ 1.5.2                │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ helmet               │ GHSA-C3M8-X3CG-QM2C  │ MEDIUM               │ 2.3.0                │ 2.4.0                │ 2.4.0                │                      │\n',
        '\t│ ├─ debug             │ CVE-2017-16137       │ MEDIUM               │ 2.2.0                │ 2.4.0                │                      │                      │\n',
        '\t│ └─ helmet-csp        │ GHSA-C3M8-X3CG-QM2C  │ MEDIUM               │ 1.2.2                │                      │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ marked               │ CVE-2022-21681       │ HIGH                 │ 0.3.9                │ 4.0.10               │ 4.0.10               │                      │\n',
        '\t│                      │ CVE-2022-21680       │ HIGH                 │                      │ 4.0.10               │                      │                      │\n',
        '\t│                      │ PRISMA-2021-0013     │ MEDIUM               │                      │ 1.1.1                │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ mocha                │ PRISMA-2022-0230     │ HIGH                 │ 2.5.3                │ N/A                  │ N/A                  │                      │\n',
        '\t│                      │ PRISMA-2022-0335     │ MEDIUM               │                      │ N/A                  │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ mongodb              │ GHSA-MH5C-679W-HH4R  │ HIGH                 │ 2.2.36               │ 3.1.13               │ 3.1.13               │                      │\n',
        '\t│ └─ bson              │ CVE-2020-7610        │ CRITICAL             │ 1.0.9                │                      │                      │                      │\n',
        '\t│                      │ CVE-2019-2391        │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ swig                 │                      │                      │ 1.4.2                │                      │ N/A                  │                      │\n',
        '\t│ ├─ minimist          │ CVE-2021-44906       │ CRITICAL             │ 0.0.10               │                      │                      │                      │\n',
        '\t│ │                    │ CVE-2020-7598        │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t│ └─ uglify-js         │ CVE-2015-8858        │ HIGH                 │ 2.4.24               │                      │                      │                      │\n',
        '\t│                      │ PRISMA-2021-0169     │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n'
    ])


def test_create_cli_output_without_dependencies():
    # given
    rootless_file_path = "package.json"
    file_abs_path = "/path/to/package.json"
    check_class = "checkov.sca_package_2.scanner.Scanner"
    # when
    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details,
            licenses='Unknown',
            package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
            root_package={'name': details["packageName"], 'version': details["packageVersion"]},
            used_private_registry=False
        )
        for details in get_vulnerabilities_details_no_deps()
    ]

    cli_output = create_cli_output(True, cves_records)
    # then

    assert cli_output == "".join(
        ["\t/package.json - CVEs Summary:\n",
         '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
         '\t│ Total CVEs: 3        │ critical: 0          │ high: 2              │ medium: 1            │ low: 0               │ skipped: 0           │ Total Packages Used: │\n',
         '\t│                      │                      │                      │                      │                      │                      │ 0                    │\n',
         '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
         '\t│ To fix 3/3 CVEs, go to your Prisma Cloud account                                                                                                               │\n',
         '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
         "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
         '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
         '\t│ marked               │ CVE-2022-21681       │ HIGH                 │ 0.3.9                │ 4.0.10               │ 4.0.10               │                      │\n',
         '\t│                      │ CVE-2022-21680       │ HIGH                 │                      │ 4.0.10               │                      │                      │\n',
         '\t│                      │ PRISMA-2021-0013     │ MEDIUM               │                      │ 1.1.1                │                      │                      │\n',
         '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n'
         ]
    )

def test_create_cli_table_for_package_with_diff_CVEs():
    # given
    rootless_file_path = "package-lock.json"
    file_abs_path = "/path/to/package-lock.json"
    check_class = "checkov.sca_package_2.scanner.Scanner"
    # when

    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details["details"],
            licenses='Unknown',
            package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
            root_package={'name': details["root_package_name"], 'version': details["root_package_version"]},
            used_private_registry=False,
            root_package_cve={'fixVersion': details.get('root_package_fix_version')}
        )
        for details in get_vulnerabilities_details_package_lock_json()
    ]

    cli_output = create_cli_output(True, cves_records)
    # then
    assert cli_output == "".join([
        "\t/package-lock.json - CVEs Summary:\n",
        '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
        '\t│ Total CVEs: 27       │ critical: 4          │ high: 11             │ medium: 11           │ low: 1               │ skipped: 0           │ Total Packages Used: │\n',
        '\t│                      │                      │                      │                      │                      │                      │ 0                    │\n',
        '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
        '\t│ To fix 25/27 CVEs, go to your Prisma Cloud account                                                                                                             │\n',
        '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
        "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ cypress              │ PRISMA-2021-0070     │ MEDIUM               │ 3.8.3                │ 7.2.0                │ 7.2.0                │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ forever              │                      │                      │ 2.0.0                │                      │ N/A                  │                      │\n',
        '\t│ ├─ decode-uri-       │ CVE-2022-38900       │ LOW                  │ 0.2.0                │                      │                      │                      │\n',
        '\t│ component            │                      │                      │                      │                      │                      │                      │\n',
        '\t│ ├─ glob-parent       │ CVE-2020-28469       │ HIGH                 │ 3.1.0                │                      │                      │                      │\n',
        '\t│ ├─ minimist          │ CVE-2021-44906       │ CRITICAL             │ 0.0.10               │                      │                      │                      │\n',
        '\t│ │                    │ CVE-2020-7598        │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t│ ├─ minimist          │ CVE-2021-44906       │ CRITICAL             │ 1.2.5                │                      │                      │                      │\n',
        '\t│ ├─ nconf             │ CVE-2022-21803       │ HIGH                 │ 0.10.0               │                      │                      │                      │\n',
        '\t│ ├─ nconf             │ CVE-2022-21803       │ HIGH                 │ 0.6.9                │                      │                      │                      │\n',
        '\t│ │                    │ CVE-2002-21803       │ HIGH                 │                      │                      │                      │                      │\n',
        '\t│ └─ unset-value       │ PRISMA-2022-0049     │ HIGH                 │ 1.0.0                │                      │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ grunt                │ CVE-2022-1537        │ HIGH                 │ 1.4.1                │ 1.5.3                │ 1.5.3                │                      │\n',
        '\t│                      │ CVE-2022-0436        │ MEDIUM               │                      │ 1.5.2                │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ helmet               │ GHSA-C3M8-X3CG-QM2C  │ MEDIUM               │ 2.3.0                │ 2.4.0                │ 2.4.0                │                      │\n',
        '\t│ ├─ debug             │ CVE-2017-16137       │ MEDIUM               │ 2.2.0                │ 2.4.0                │                      │                      │\n',
        '\t│ └─ helmet-csp        │ GHSA-C3M8-X3CG-QM2C  │ MEDIUM               │ 1.2.2                │                      │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ marked               │ CVE-2022-21681       │ HIGH                 │ 0.3.9                │ 4.0.10               │ 4.0.10               │                      │\n',
        '\t│                      │ CVE-2022-21680       │ HIGH                 │                      │ 4.0.10               │                      │                      │\n',
        '\t│                      │ PRISMA-2021-0013     │ MEDIUM               │                      │ 1.1.1                │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ mocha                │ PRISMA-2022-0230     │ HIGH                 │ 2.5.3                │ N/A                  │ N/A                  │                      │\n',
        '\t│                      │ PRISMA-2022-0335     │ MEDIUM               │                      │ N/A                  │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ mongodb              │ GHSA-MH5C-679W-HH4R  │ HIGH                 │ 2.2.36               │ 3.1.13               │ 3.1.13               │                      │\n',
        '\t│ └─ bson              │ CVE-2020-7610        │ CRITICAL             │ 1.0.9                │                      │                      │                      │\n',
        '\t│                      │ CVE-2019-2391        │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
        '\t│ swig                 │                      │                      │ 1.4.2                │                      │ N/A                  │                      │\n',
        '\t│ ├─ minimist          │ CVE-2021-44906       │ CRITICAL             │ 0.0.10               │                      │                      │                      │\n',
        '\t│ │                    │ CVE-2020-7598        │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t│ └─ uglify-js         │ CVE-2015-8858        │ HIGH                 │ 2.4.24               │                      │                      │                      │\n',
        '\t│                      │ PRISMA-2021-0169     │ MEDIUM               │                      │                      │                      │                      │\n',
        '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n'])


def test_create_cli_table_for_package_with_reachability_data():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package_2.scanner.Scanner"
    # when
    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details,
            licenses='Unknown',
            package={'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False},
            root_package={'name': details["packageName"], 'version': details["packageVersion"]},
            used_private_registry=False
        )
        for details in get_vulnerabilities_details_is_used_packages()
    ]
    cli_output = create_cli_output(True, cves_records)
    with open(os.path.join(CLI_OUTPUTS_DIR, "test_create_cli_table_for_package_with_reachability_data.txt")) as f:
        expected_cli_output = f.read()
    assert expected_cli_output == cli_output
