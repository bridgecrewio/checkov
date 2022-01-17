from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Union, Dict, Any

from packaging import version as packaging_version
from prettytable import PrettyTable, SINGLE_BORDER


def create_vulnerabilities_record(
    vulnerabilities: List[Dict[str, Any]], vulnerability_dist: Dict[str, int]
) -> Dict[str, Any]:
    result = {
        "count": {
            "total": vulnerability_dist["total"],
            "critical": vulnerability_dist["critical"],
            "high": vulnerability_dist["high"],
            "medium": vulnerability_dist["medium"],
            "low": vulnerability_dist["low"],
            "skipped": 0,  # ToDo: needs to be adjusted, when skipping is supported
        }
    }

    fixable_cves = 0
    package_vulnerabilities = defaultdict(dict)
    package_fixed_version_map: Dict[
        str, List[List[Union[packaging_version.Version, packaging_version.LegacyVersion]]]
    ] = {}
    for idx, vul in enumerate(vulnerabilities):
        fixed_version = "N/A"
        package_name = vul["packageName"]
        status = vul.get("status") or "open"
        if status != "open":
            fixed_versions = [
                packaging_version.parse(version.strip()) for version in status.replace("fixed in", "").split(",")
            ]
            fixed_version = str(min(fixed_versions))
            package_fixed_version_map.setdefault(package_name, []).append(fixed_versions)
            fixable_cves += 1

        vulnerability = {
            "id": vul.get("id"),
            "status": status,
            "severity": vul.get("severity"),
            "link": vul.get("link"),
            "cvss": vul.get("cvss"),
            "vector": vul.get("vector"),
            "description": vul.get("description"),
            "risk_factors": vul.get("riskFactors"),
            "published_date": vul.get("publishedDate")
            or (datetime.now() - timedelta(days=vul.get("publishedDays", 0))).isoformat(),
            "fixed_version": fixed_version,
        }
        package_vulnerabilities[package_name].setdefault("cves", []).append(vulnerability)
        package_vulnerabilities[package_name]["complaint_version"] = "N/A"
        if not package_vulnerabilities[package_name].get("current_version"):
            package_vulnerabilities[package_name]["current_version"] = vul.get("packageVersion")

    if package_fixed_version_map:
        for package_name, fix_versions_lists in package_fixed_version_map.items():
            package_vulnerabilities[package_name]["complaint_version"] = calculate_lowest_complaint_version(
                fix_versions_lists
            )

    result["count"]["fixable"] = fixable_cves
    result["packages"] = package_vulnerabilities

    return result


def calculate_lowest_complaint_version(
    fix_versions_lists: List[List[Union[packaging_version.Version, packaging_version.LegacyVersion]]]
) -> str:
    """A best effort approach to find the lowest complaint version"""

    package_min_versions = set()
    package_versions = set()

    for fix_versions in fix_versions_lists:
        package_min_versions.add(min(fix_versions))
        package_versions.update(fix_versions)
    package_min_version = min(package_min_versions)
    package_max_version = max(package_min_versions)

    if isinstance(package_min_version, packaging_version.LegacyVersion) or isinstance(
        package_max_version, packaging_version.LegacyVersion
    ):
        return str(package_max_version)
    elif package_min_version.major == package_max_version.major:
        return str(package_max_version)
    else:
        lowest_version = max(
            version
            for version in package_versions
            if isinstance(version, packaging_version.Version) and version.major == package_max_version.major
        )
        return str(lowest_version)


def create_cli_table(file_path: str, vulnerabilities: Dict[str, Any]) -> str:
    columns = 6
    table_width = 120
    column_width = 120 / columns
    cve_table = PrettyTable(
        header=False,
        padding_width=1,
        min_table_width=table_width,
        max_table_width=table_width,
    )
    cve_table.set_style(SINGLE_BORDER)
    cve_table.add_row(
        [
            f"Total CVE: {vulnerabilities['count']['total']}",
            f"critical: {vulnerabilities['count']['critical']}",
            f"high: {vulnerabilities['count']['high']}",
            f"medium: {vulnerabilities['count']['medium']}",
            f"low: {vulnerabilities['count']['low']}",
            f"skipped: {vulnerabilities['count']['skipped']}",
        ]
    )
    cve_table.align = "l"
    cve_table.min_width = column_width
    cve_table.max_width = column_width

    cve_table_lines = [f"\t{line}" for line in cve_table.get_string().splitlines(keepends=True)]
    # hack to make multiple tables look like one
    cve_table_bottom_line = (
        cve_table_lines[-1]
        .replace(cve_table.bottom_left_junction_char, cve_table.left_junction_char)
        .replace(cve_table.bottom_right_junction_char, cve_table.right_junction_char)
    )
    cve_table_lines[-1] = cve_table_bottom_line

    fixable_table = PrettyTable(
        header=False, min_table_width=table_width + columns * 2, max_table_width=table_width + columns * 2
    )
    fixable_table.set_style(SINGLE_BORDER)
    fixable_table.add_row(
        [
            f"To fix {vulnerabilities['count']['fixable']}/{vulnerabilities['count']['total']} CVEs, go to https://www.bridgecrew.cloud/"
        ]
    )
    fixable_table.align = "l"

    # hack to make multiple tables look like one
    fixable_table_lines = [f"\t{line}" for line in fixable_table.get_string().splitlines(keepends=True)]
    del fixable_table_lines[0]
    # only remove the last line, if there are vulnerable packages
    if vulnerabilities["packages"]:
        del fixable_table_lines[-1]

    package_table_lines: List[str] = []
    package_table = PrettyTable(min_table_width=table_width, max_table_width=table_width)
    package_table.set_style(SINGLE_BORDER)
    package_table.field_names = [
        "Package",
        "CVE ID",
        "Severity",
        "Current version",
        "Fixed version",
        "Complaint version",
    ]
    for package_idx, (package_name, details) in enumerate(vulnerabilities["packages"].items()):
        if package_idx > 0:
            del package_table_lines[-1]
            package_table.header = False
            package_table.clear_rows()

        for cve_idx, cve in enumerate(details["cves"]):
            col_package = ""
            col_current_version = ""
            col_complaint_version = ""
            if cve_idx == 0:
                col_package = package_name
                col_current_version = details["current_version"]
                col_complaint_version = details["complaint_version"]

            package_table.add_row(
                [
                    col_package,
                    cve["id"],
                    cve["severity"],
                    col_current_version,
                    cve["fixed_version"],
                    col_complaint_version,
                ]
            )

        package_table.align = "l"
        package_table.min_width = column_width
        package_table.max_width = column_width

        for idx, line in enumerate(package_table.get_string().splitlines(keepends=True)):
            if idx == 0:
                # hack to make multiple tables look like one
                line = line.replace(package_table.top_left_junction_char, package_table.left_junction_char).replace(
                    package_table.top_right_junction_char, package_table.right_junction_char
                )
            if package_idx > 0:
                # hack to make multiple package tables look like one
                line = line.replace(package_table.top_junction_char, package_table.junction_char)

            package_table_lines.append(f"\t{line}")

    package_table = PrettyTable(min_table_width=table_width, max_table_width=table_width)
    package_table.set_style(SINGLE_BORDER)
    package_table.field_names = [
        "Package",
        "CVE ID",
        "Severity",
        "Current version",
        "Fixed version",
        "Complaint version",
    ]
    package_table.header = False
    package_table.clear_rows()
    for package_name, details in vulnerabilities["packages"].items():
        for idx, cve in enumerate(details["cves"]):
            col_package = ""
            col_current_version = ""
            col_complaint_version = ""
            if idx == 0:
                col_package = package_name
                col_current_version = details["current_version"]
                col_complaint_version = details["complaint_version"]

            package_table.add_row(
                [
                    col_package,
                    cve["id"],
                    cve["severity"],
                    col_current_version,
                    cve["fixed_version"],
                    col_complaint_version,
                ]
            )
    package_table.align = "l"
    package_table.min_width = column_width
    package_table.max_width = column_width

    return (
        f"\t{file_path}\n"
        f"{''.join(cve_table_lines)}\n"
        f"{''.join(fixable_table_lines)}"
        f"{''.join(package_table_lines)}"
    )
