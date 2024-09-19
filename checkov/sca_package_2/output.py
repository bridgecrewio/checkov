from __future__ import annotations

import itertools
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Union, Dict, Any

from prettytable import PrettyTable, SINGLE_BORDER

from checkov.common.bridgecrew.severities import BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record, SCA_PACKAGE_SCAN_CHECK_NAME, SCA_LICENSE_CHECK_NAME
from checkov.common.output.common import get_package_name_with_lines, validate_lines, get_reachability_output_indication
from checkov.common.packaging import version as packaging_version
from checkov.common.sca.commons import UNFIXABLE_VERSION, get_package_alias
from checkov.common.typing import _LicenseStatusWithLines
from checkov.common.output.common import compare_table_items_severity

REACHABILITY_RISK_FACTORS_KEYS = ["IsUsed", "ReachableFunction"]


@dataclass
class CveCount:
    total: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    skipped: int = 0
    used: int = 0
    has_fix: int = 0
    to_fix: int = 0
    fixable: bool = True

    def output_row(self) -> List[str]:
        return [
            f"Total CVEs: {self.total}",
            f"critical: {self.critical}",
            f"high: {self.high}",
            f"medium: {self.medium}",
            f"low: {self.low}",
            f"skipped: {self.skipped}",
            f"Total Packages Used: {self.used}",
        ]


def calculate_lowest_compliant_version(
        fix_versions_lists: List[List[Union[packaging_version.Version, packaging_version.LegacyVersion]]]
) -> str:
    """A best effort approach to find the lowest compliant version"""

    package_min_versions = set()
    package_versions = set()

    for fix_versions in fix_versions_lists:
        if fix_versions:
            package_min_versions.add(min(fix_versions))
            package_versions.update(fix_versions)
    if package_min_versions:
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

    return UNFIXABLE_VERSION


def create_cli_output(fixable: bool = True, *cve_records: list[Record]) -> str:
    cli_outputs = []
    group_by_file_path_package_map: dict[str, dict[str, list[Record]]] = defaultdict(dict)

    for record in itertools.chain(*cve_records):
        if not record.vulnerability_details:
            #  this shouldn't happen
            logging.error(f"'vulnerability_details' is not set for {record.check_id}")
            continue

        if record.vulnerability_details.get("root_package_name"):
            _root_package_alias = get_package_alias(
                record.vulnerability_details["root_package_name"],
                record.vulnerability_details["root_package_version"])

        else:  # in case it's license record
            _root_package_alias = get_package_alias(record.vulnerability_details["package_name"],
                                                    record.vulnerability_details["package_version"])

        group_by_file_path_package_map[record.file_path].setdefault(
            _root_package_alias, []).append(record)

    for file_path, packages in group_by_file_path_package_map.items():
        cve_count = CveCount(fixable=fixable)
        package_cves_details_map: dict[str, dict[str, Any]] = defaultdict(dict)
        package_licenses_details_map = defaultdict(list)
        should_print_licenses_table = False
        lines_details_found_cves = False
        lines_details_found_licenses = False
        for root_package_alias, records in packages.items():
            fix_versions_lists = []
            for record in records:
                if not record.vulnerability_details:
                    #  this shouldn't happen
                    logging.error(f"'vulnerability_details' is not set for {record.check_id}")
                    continue

                package_name = record.vulnerability_details["package_name"]
                package_version = record.vulnerability_details["package_version"]
                lines = validate_lines(record.file_line_range)

                if record.check_name == SCA_PACKAGE_SCAN_CHECK_NAME:
                    cve_count.total += 1

                    if record.check_result["result"] == CheckResult.SKIPPED:
                        cve_count.skipped += 1
                        continue
                    else:
                        cve_count.to_fix += 1

                    # best way to dynamically access a class instance attribute.
                    # (we can't just do cve_count.severity_str to access the correct severity)
                    severity_str = record.severity.name.upper() if record.severity else BcSeverities.NONE.upper()
                    setattr(cve_count, severity_str.lower(), getattr(cve_count, severity_str.lower()) + 1)

                    if record.vulnerability_details["lowest_fixed_version"] != UNFIXABLE_VERSION:
                        cve_count.has_fix += 1

                    is_root_package = root_package_alias == get_package_alias(package_name, package_version)
                    if is_root_package:  # we want fixed versions just for root packages
                        fix_versions_lists.append(record.vulnerability_details["fixed_versions"])
                    else:
                        root_package_fix_version = record.vulnerability_details.get("root_package_fix_version")
                        if root_package_fix_version:
                            parsed_version = packaging_version.parse(root_package_fix_version.strip())
                            fix_versions_lists.append([parsed_version])

                    root_package_lines = validate_lines(
                        record.vulnerability_details.get("root_package_file_line_range"))
                    if lines or root_package_lines:
                        lines_details_found_cves = True

                    risk_factors = {} if not record.vulnerability_details or not record.vulnerability_details.get("risk_factors", {}) else record.vulnerability_details.get("risk_factors", {})

                    reachability_risk_factors_tmp = {key: value for key, value in risk_factors.items()
                                                     if key in REACHABILITY_RISK_FACTORS_KEYS}
                    if any([value for value in reachability_risk_factors_tmp.values()]):
                        cve_count.used += 1

                    package_cves_details_map[root_package_alias].setdefault("cves", []).append(
                        {
                            "id": record.vulnerability_details["id"],
                            "severity": severity_str,
                            "fixed_version": record.vulnerability_details["lowest_fixed_version"],
                            "root_package_name": record.vulnerability_details["root_package_name"],
                            "root_package_version": record.vulnerability_details["root_package_version"],
                            "root_package_fix_version": record.vulnerability_details.get("root_package_fix_version",
                                                                                         ""),
                            "package_name": package_name,
                            "package_version": package_version,
                            "lines": lines,
                            "root_package_lines": root_package_lines,
                            "is_private_fix": record.vulnerability_details.get("is_private_fix"),
                            "reachability_risk_factors": reachability_risk_factors_tmp
                        }
                    )
                elif record.check_name == SCA_LICENSE_CHECK_NAME:
                    if record.check_result["result"] == CheckResult.SKIPPED:
                        continue
                    should_print_licenses_table = True
                    if lines:
                        lines_details_found_licenses = True
                    package_licenses_details_map[get_package_alias(package_name, package_version)].append(
                        _LicenseStatusWithLines(package_name=package_name,
                                                package_version=package_version,
                                                policy=record.vulnerability_details["policy"],
                                                license=record.vulnerability_details["license"],
                                                status=record.vulnerability_details["status"],
                                                lines=lines)
                    )

            if root_package_alias in package_cves_details_map:
                package_cves_details_map[root_package_alias]["cves"].sort(key=compare_table_items_severity,
                                                                          reverse=True)
                package_cves_details_map[root_package_alias]["compliant_version"] = calculate_lowest_compliant_version(
                    fix_versions_lists)

        if cve_count.total > 0:
            cli_outputs.append(
                create_cli_cves_table(
                    file_path=file_path,
                    cve_count=cve_count,
                    package_details_map=package_cves_details_map,
                    lines_details_found=lines_details_found_cves
                )
            )
        if should_print_licenses_table:
            cli_outputs.append(
                create_cli_license_violations_table(
                    file_path=file_path,
                    package_licenses_details_map=package_licenses_details_map,
                    lines_details_found=lines_details_found_licenses
                )
            )
    return "\n".join(cli_outputs)


def create_cli_license_violations_table(file_path: str,
                                        package_licenses_details_map: Dict[str, List[_LicenseStatusWithLines]],
                                        lines_details_found: bool) -> str:
    package_table_lines: List[str] = []
    columns = 5
    table_width = 136
    column_width = int(table_width / columns)
    package_table = PrettyTable(min_table_width=table_width, max_table_width=table_width)
    package_table.set_style(SINGLE_BORDER)
    package_table.field_names = [
        "Package name [Lines]" if lines_details_found else "Package name",
        "Package version",
        "Policy ID",
        "License",
    ]
    for package_idx, (_, license_statuses) in enumerate(package_licenses_details_map.items()):
        if package_idx > 0:
            del package_table_lines[-1]
            package_table.header = False
            package_table.clear_rows()

        for idx, license_status in enumerate(license_statuses):
            col_package_name = ""
            col_package_version = ""
            if idx == 0:
                col_package_name = get_package_name_with_lines(license_status["package_name"], license_status["lines"])
                col_package_version = license_status["package_version"]

            curr_row = [
                col_package_name,
                col_package_version,
                license_status["policy"],
                license_status["license"]
            ]
            package_table.add_row(curr_row)

        package_table.align = "l"
        package_table.min_width = column_width
        package_table.max_width = column_width

        for idx, line in enumerate(package_table.get_string().splitlines(keepends=True)):
            if idx == 0 and package_idx != 0:
                # hack to make multiple tables look like one
                line = line.replace(package_table.top_left_junction_char, package_table.left_junction_char).replace(
                    package_table.top_right_junction_char, package_table.right_junction_char
                )
            if package_idx > 0:
                # hack to make multiple package tables look like one
                line = line.replace(package_table.top_junction_char, package_table.junction_char)

            # hack for making the table's width as same as the cves-table's
            package_table_lines.append(f"\t{line[:-2]}{line[-3]}{line[-2:]}")

    return (
        f"\t{file_path} - Licenses Statuses:\n"
        f"{''.join(package_table_lines)}\n"
    )


def create_cli_cves_table(file_path: str, cve_count: CveCount, package_details_map: Dict[str, Dict[str, Any]],
                          lines_details_found: bool) -> str:
    columns = 7
    table_width = 165
    fixed_line_with = 159
    column_width = int(table_width / columns)

    cve_table_lines = create_cve_summary_table_part(
        table_width=table_width, column_width=column_width, cve_count=cve_count
    )

    vulnerable_packages = True if package_details_map else False
    fixable_table_lines = create_fixable_cve_summary_table_part(
        table_width=fixed_line_with, column_count=columns, cve_count=cve_count, vulnerable_packages=vulnerable_packages
    )

    package_table_lines = create_package_overview_table_part(
        table_width=table_width, column_width=column_width, package_details_map=package_details_map,
        lines_details_found=lines_details_found
    )

    return (
        f"\t{file_path} - CVEs Summary:\n"
        f"{''.join(cve_table_lines)}\n"
        f"{''.join(fixable_table_lines)}"
        f"{''.join(package_table_lines)}\n"
    )


def create_cve_summary_table_part(table_width: int, column_width: int, cve_count: CveCount) -> List[str]:
    cve_table = PrettyTable(
        header=False,
        padding_width=1,
        min_table_width=table_width,
        max_table_width=table_width,
    )
    cve_table.set_style(SINGLE_BORDER)
    cve_table.add_row(cve_count.output_row())
    cve_table.align = "l"
    cve_table.min_width = column_width
    cve_table.max_width = column_width

    cve_table_lines = [f"\t{line}" for line in cve_table.get_string().splitlines(keepends=True)]
    # hack to make multiple tables look like one
    cve_table_bottom_line = (
        cve_table_lines[-1].replace(cve_table.bottom_left_junction_char,
                                    cve_table.left_junction_char).replace(cve_table.bottom_right_junction_char,
                                                                          cve_table.right_junction_char)
    )
    cve_table_lines[-1] = cve_table_bottom_line

    return cve_table_lines


def create_fixable_cve_summary_table_part(
        table_width: int, column_count: int, cve_count: CveCount, vulnerable_packages: bool
) -> List[str]:
    fixable_table = PrettyTable(
        header=False,
        min_table_width=table_width + column_count - 4,
        max_table_width=table_width + column_count - 4
    )
    fixable_table.set_style(SINGLE_BORDER)
    if cve_count.fixable:
        fixable_table.add_row(
            [f"To fix {cve_count.has_fix}/{cve_count.to_fix} CVEs, go to your Prisma Cloud account"])
        fixable_table.align = "l"
    else:
        return []

    # hack to make multiple tables look like one
    fixable_table_lines = [f"\t{line}" for line in fixable_table.get_string().splitlines(keepends=True)]
    del fixable_table_lines[0]
    # only remove the last line, if there are vulnerable packages
    if vulnerable_packages:
        del fixable_table_lines[-1]

    return fixable_table_lines


def create_package_overview_table_part(
        table_width: int, column_width: int, package_details_map: Dict[str, Dict[str, Any]], lines_details_found: bool
) -> str | Any:
    package_table_lines: List[str] = []
    package_table = PrettyTable(min_table_width=table_width, max_table_width=table_width)
    package_table.set_style(SINGLE_BORDER)
    package_table.field_names = [
        "Package [Lines]" if lines_details_found else "Package",
        "CVE ID",
        "Severity",
        "Current version",
        "Root fixed version",
        "Compliant version",
        "Reachability"
    ]
    for package_idx, (root_package_alias, details) in enumerate(package_details_map.items()):
        if package_idx > 0:
            del package_table_lines[-1]
            package_table.header = False
            package_table.clear_rows()

        details["cves"].sort(key=lambda x: (
            "" if x["root_package_name"] == x['package_name'] else x['package_name'], x['package_version']))

        last_package_alias = get_package_alias(details['cves'][-1]['package_name'],
                                               details['cves'][-1]['package_version'])
        previous_package = ""
        for cve_idx, cve in enumerate(details["cves"]):
            compliant_version = details.get("compliant_version", "")
            package_name = cve["package_name"]
            package_version = cve["package_version"]
            package_alias = get_package_alias(package_name, package_version)
            is_root = package_alias == root_package_alias
            is_public_overview = "(Public)" if cve['is_private_fix'] is False else ""
            reachability = get_reachability_output_indication(cve.get('reachability_risk_factors', {}))
            compliant_version_overview = ""
            if cve_idx == 0:
                cur_compliant_version = compliant_version + is_public_overview if compliant_version and compliant_version != UNFIXABLE_VERSION else compliant_version
                if not is_root:  # no cves on root package
                    package_name_col_val = get_package_name_with_lines(cve["root_package_name"],
                                                                       cve.get("root_package_lines"))
                    package_table.add_row(
                        [
                            package_name_col_val,
                            "",
                            "",
                            cve["root_package_version"],
                            "",
                            cur_compliant_version,
                            ""
                        ]
                    )
                else:
                    compliant_version_overview = cur_compliant_version

            is_sub_dep_changed = previous_package != package_alias
            dep_sign = ""
            if not is_root:
                if is_sub_dep_changed:
                    if last_package_alias == package_alias:
                        dep_sign = package_table.bottom_left_junction_char + package_table.horizontal_char
                    else:
                        dep_sign = package_table.left_junction_char + package_table.horizontal_char
                else:
                    if last_package_alias != package_alias:
                        dep_sign = package_table.vertical_char

            package_name_col_val = ""
            if is_sub_dep_changed:
                if dep_sign:
                    package_name_col_val = " ".join([dep_sign, package_name])
                else:
                    package_name_col_val = package_name
                package_name_col_val = get_package_name_with_lines(package_name_col_val, cve.get("lines"))
            elif dep_sign:
                package_name_col_val = dep_sign

            fix_version = cve["fixed_version"] if is_root else cve.get("root_package_fix_version", "")
            fix_version_overview = fix_version + is_public_overview if fix_version and fix_version != UNFIXABLE_VERSION else fix_version
            package_table.add_row(
                [
                    package_name_col_val,
                    cve["id"],
                    cve["severity"],
                    package_version if is_sub_dep_changed else "",
                    fix_version_overview,
                    compliant_version_overview,
                    reachability
                ]
            )

            previous_package = package_alias

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

    return package_table_lines
