from packaging import version as packaging_version

from checkov.sca_package.output import (
    create_vulnerabilities_record,
    calculate_lowest_complaint_version,
    create_cli_table,
)


def test_create_vulnerabilities_record(vulnerabilities_and_dist):
    # given
    vulnerabilities, dist = vulnerabilities_and_dist

    # when
    record = create_vulnerabilities_record(vulnerabilities, dist)

    # then
    assert record["count"] == {"total": 6, "critical": 1, "high": 3, "medium": 2, "low": 0, "skipped": 0, "fixable": 6}
    assert "django" in record["packages"].keys()
    assert "flask" in record["packages"].keys()

    package_django = record["packages"]["django"]
    assert len(package_django["cves"]) == 4
    assert package_django["complaint_version"] == "2.2.24"
    assert package_django["current_version"] == "1.2"

    package_flask = record["packages"]["flask"]
    assert len(package_flask["cves"]) == 2
    assert package_flask["complaint_version"] == "1.0"
    assert package_flask["current_version"] == "0.6"


def test_create_vulnerabilities_record_with_no_found_vulnerabilities():
    # given
    vulnerabilities = []
    dist = {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}

    # when
    record = create_vulnerabilities_record(vulnerabilities, dist)

    # then
    assert record == {
        "count": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "skipped": 0, "fixable": 0},
        "packages": {},
    }


def test_calculate_lowest_complaint_version():
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
    complaint_version = calculate_lowest_complaint_version(fix_versions_lists)

    # then
    assert complaint_version == "2.2.24"


def test_create_cli_table(vulnerabilities_and_dist):
    # given
    file_path = "/path/to/requirements.txt"
    vulnerabilities, dist = vulnerabilities_and_dist
    record = create_vulnerabilities_record(vulnerabilities, dist)

    # when
    table = create_cli_table(file_path, record)

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVE: 6       │ critical: 1        │ high: 3            │ medium: 2          │ low: 0             │ skipped: 0         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 6/6 CVEs, go to https://www.bridgecrew.cloud/                                                                        │\n",
            "\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤\n",
            "\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Complaint version  │\n",
            "\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n",
            "\t│ django             │ CVE-2019-19844     │ critical           │ 1.2                │ 1.11.27            │ 2.2.24             │\n",
            "\t│                    │ CVE-2016-6186      │ medium             │                    │ 1.8.14             │                    │\n",
            "\t│                    │ CVE-2016-7401      │ high               │                    │ 1.8.15             │                    │\n",
            "\t│                    │ CVE-2021-33203     │ medium             │                    │ 2.2.24             │                    │\n",
            "\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n",
            "\t│ flask              │ CVE-2019-1010083   │ high               │ 0.6                │ 1.0                │ 1.0                │\n",
            "\t│                    │ CVE-2018-1000656   │ high               │                    │ 0.12.3             │                    │\n",
            "\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘",
        ]
    )


def test_create_cli_table_with_no_found_vulnerabilities():
    # given
    file_path = "/path/to/requirements.txt"
    vulnerabilities = {
        "count": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "skipped": 0, "fixable": 0},
        "packages": {},
    }

    # when
    table = create_cli_table(file_path, vulnerabilities)

    # then
    assert table == "".join(
        [
            "\t/path/to/requirements.txt\n",
            "\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n",
            "\t│ Total CVE: 0       │ critical: 0        │ high: 0            │ medium: 0          │ low: 0             │ skipped: 0         │\n",
            "\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤\n",
            "\t│ To fix 0/0 CVEs, go to https://www.bridgecrew.cloud/                                                                        │\n",
            "\t└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘",
        ]
    )
