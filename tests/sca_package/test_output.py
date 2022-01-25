from packaging import version as packaging_version

from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.output import (
    calculate_lowest_compliant_version,
    create_cli_table,
    create_report_record,
    create_cli_output,
    compare_cve_severity,
    CveCount,
)


def test_create_report_record():
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
    record = create_report_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
    )

    # then
    assert record.bc_check_id == "BC_CVE_2019_19844"
    assert record.check_id == "CKV_CVE_2019_19844"
    assert record.check_class == check_class
    assert record.check_name == "SCA package scan"
    assert record.check_result == {"result": CheckResult.FAILED}
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
    assert record.severity == "critical"
    assert record.short_description == "CVE-2019-19844 - django: 1.2"
    assert record.vulnerability_details["lowest_fixed_version"] == "1.11.27"
    assert record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("3.0.1"),
        packaging_version.parse("2.2.9"),
        packaging_version.parse("1.11.27"),
    ]


def test_create_report_record_severity_filter():
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
    record = create_report_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        runner_filter=RunnerFilter(min_cve_severity='high')
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
    assert record.severity == "medium"
    assert record.short_description == "CVE-2019-19844 - django: 1.2"
    assert record.vulnerability_details["lowest_fixed_version"] == "1.11.27"
    assert record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("3.0.1"),
        packaging_version.parse("2.2.9"),
        packaging_version.parse("1.11.27"),
    ]


def test_create_report_record_package_filter():
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
    record = create_report_record(
        rootless_file_path=rootless_file_path,
        file_abs_path=file_abs_path,
        check_class=check_class,
        vulnerability_details=vulnerability_details,
        runner_filter=RunnerFilter(skip_cve_package=['django', 'requests'])
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
    assert record.severity == "critical"
    assert record.short_description == "CVE-2019-19844 - django: 1.2"
    assert record.vulnerability_details["lowest_fixed_version"] == "1.11.27"
    assert record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("3.0.1"),
        packaging_version.parse("2.2.9"),
        packaging_version.parse("1.11.27"),
    ]


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


def test_create_cli_table():
    # given
    file_path = "/path/to/requirements.txt"
    cve_count = CveCount(total=6, critical=0, high=3, medium=2, low=0, skipped=1, fixable=5, to_fix=5)
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
    table = create_cli_table(
        file_path=file_path,
        cve_count=cve_count,
        package_details_map=package_details_map,
    )

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVEs: 6      │ critical: 0        │ high: 3            │ medium: 2          │ low: 0             │ skipped: 1         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 5/5 CVEs, go to https://www.bridgecrew.cloud/                                                                        │\n",
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


def test_create_cli_table_with_no_found_vulnerabilities():
    # given
    file_path = "/path/to/requirements.txt"
    cve_count = CveCount(total=2, critical=0, high=0, medium=0, low=0, skipped=2, fixable=0, to_fix=0)
    package_details_map = {}

    # when
    table = create_cli_table(
        file_path=file_path,
        cve_count=cve_count,
        package_details_map=package_details_map,
    )

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVEs: 2      │ critical: 0        │ high: 0            │ medium: 0          │ low: 0             │ skipped: 2         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 0/0 CVEs, go to https://www.bridgecrew.cloud/                                                                        │\n",
            "\t└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘\n",
        ]
    )


def test_create_cli_output():
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    vulnerabilities_details = [
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

    # when
    records = [
        create_report_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details,
        )
        for details in vulnerabilities_details
    ]

    # when
    cli_output = create_cli_output(records)

    # then
    assert cli_output == "".join(
        [
            "\t/requirements.txt\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVEs: 2      │ critical: 1        │ high: 0            │ medium: 1          │ low: 0             │ skipped: 0         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 2/2 CVEs, go to https://www.bridgecrew.cloud/                                                                        │\n",
            "\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤\n",
            "\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │\n",
            "\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n",
            "\t│ django             │ CVE-2019-19844     │ critical           │ 1.2                │ 1.11.27            │ 1.11.27            │\n",
            "\t│                    │ CVE-2016-6186      │ medium             │                    │ 1.8.14             │                    │\n",
            "\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘\n",
        ]
    )


def test_compare_cve_severity():
    # given
    cve = [
        {"id": "CVE-2016-6186", "severity": "medium", "fixed_version": "1.8.14"},
        {"id": "CVE-2016-7401", "severity": "high", "fixed_version": "1.8.15"},
        {"id": "CVE-2021-33203", "severity": "medium", "fixed_version": "2.2.24"},
        {"id": "CVE-2019-19844", "severity": "critical", "fixed_version": "1.11.27"},
    ]

    # when
    cve.sort(key=compare_cve_severity)

    # then
    assert cve == [
        {"id": "CVE-2019-19844", "severity": "critical", "fixed_version": "1.11.27"},
        {"id": "CVE-2016-7401", "severity": "high", "fixed_version": "1.8.15"},
        {"id": "CVE-2016-6186", "severity": "medium", "fixed_version": "1.8.14"},
        {"id": "CVE-2021-33203", "severity": "medium", "fixed_version": "2.2.24"},
    ]
