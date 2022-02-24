import asyncio
import itertools
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Union, Dict, Any, Sequence
import os
import logging
from aiomultiprocess import Pool

from packaging import version as packaging_version
from prettytable import PrettyTable, SINGLE_BORDER

from checkov.common.bridgecrew.severities import Severities
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record, DEFAULT_SEVERITY
from checkov.common.typing import _CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.common.bridgecrew.vulnerability_scanning.integrations.package_scanning import PackageScanningIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration

UNFIXABLE_VERSION = "N/A"


@dataclass
class CveCount:
    total: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    skipped: int = 0
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
        ]


def create_report_record(
    rootless_file_path: str, file_abs_path: str, check_class: str, vulnerability_details: Dict[str, Any],
    runner_filter: RunnerFilter = RunnerFilter()
) -> Record:
    package_name = vulnerability_details["packageName"]
    package_version = vulnerability_details["packageVersion"]
    cve_id = vulnerability_details["id"].upper()
    severity = vulnerability_details.get("severity", DEFAULT_SEVERITY)
    # sanitize severity names
    if severity == "moderate":
        severity = "medium"
    description = vulnerability_details.get("description")
    resource = f"{rootless_file_path}.{package_name}"

    check_result: _CheckResult = {
        "result": CheckResult.FAILED,
    }

    if runner_filter.skip_cve_package and package_name in runner_filter.skip_cve_package:
        check_result = {
            "result": CheckResult.SKIPPED,
            "suppress_comment": f"Filtered by package '{package_name}'"
        }
    elif not runner_filter.within_threshold(Severities[severity.upper()]):
        check_result = {
            "result": CheckResult.SKIPPED,
            "suppress_comment": "Filtered by severity"
        }

    code_block = [(0, f"{package_name}: {package_version}")]

    lowest_fixed_version = UNFIXABLE_VERSION
    fixed_versions: List[Union[packaging_version.Version, packaging_version.LegacyVersion]] = []
    status = vulnerability_details.get("status") or "open"
    if status != "open":
        fixed_versions = [
            packaging_version.parse(version.strip()) for version in status.replace("fixed in", "").split(",")
        ]
        lowest_fixed_version = str(min(fixed_versions))


    details = {
        "id": cve_id,
        "status": status,
        "severity": severity,
        "package_name": package_name,
        "package_version": package_version,
        "link": vulnerability_details.get("link"),
        "cvss": vulnerability_details.get("cvss"),
        "vector": vulnerability_details.get("vector"),
        "description": description,
        "risk_factors": vulnerability_details.get("riskFactors"),
        "published_date": vulnerability_details.get("publishedDate")
        or (datetime.now() - timedelta(days=vulnerability_details.get("publishedDays", 0))).isoformat(),
        "lowest_fixed_version": lowest_fixed_version,
        "fixed_versions": fixed_versions,
    }

    record = Record(
        check_id=f"CKV_{cve_id.replace('-', '_')}",
        bc_check_id=f"BC_{cve_id.replace('-', '_')}",
        check_name="SCA package scan",
        check_result=check_result,
        code_block=code_block,
        file_path=f"/{rootless_file_path}",
        file_line_range=[0, 0],
        resource=resource,
        check_class=check_class,
        evaluations=None,
        file_abs_path=file_abs_path,
        severity=Severities[severity.upper()],
        description=description,
        short_description=f"{cve_id} - {package_name}: {package_version}",
        vulnerability_details=details,
    )
    return record


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


def compare_cve_severity(cve: Dict[str, str]) -> int:
    severity = (cve.get("severity") or DEFAULT_SEVERITY).upper()
    return Severities[severity].level


def create_cli_output(fixable=True, *cve_records: List[Record]) -> str:
    cli_outputs = []
    group_by_file_path_package_map = defaultdict(dict)

    for record in itertools.chain(*cve_records):
        group_by_file_path_package_map[record.file_path].setdefault(
            record.vulnerability_details["package_name"], []
        ).append(record)

    for file_path, packages in group_by_file_path_package_map.items():
        cve_count = CveCount(fixable=fixable)
        package_details_map = defaultdict(dict)

        for package_name, records in packages.items():
            package_version = None
            fix_versions_lists = []

            for record in records:
                cve_count.total += 1

                if record.check_result["result"] == CheckResult.SKIPPED:
                    cve_count.skipped += 1
                    continue
                else:
                    cve_count.to_fix += 1

                # best way to dynamically access an class instance attribute
                severity_str = record.severity.name.lower()
                setattr(cve_count, severity_str, getattr(cve_count, severity_str) + 1)

                if record.vulnerability_details["lowest_fixed_version"] != UNFIXABLE_VERSION:
                    cve_count.has_fix += 1

                fix_versions_lists.append(record.vulnerability_details["fixed_versions"])
                if package_version is None:
                    package_version = record.vulnerability_details["package_version"]

                package_details_map[package_name].setdefault("cves", []).append(
                    {
                        "id": record.vulnerability_details["id"],
                        "severity": severity_str,
                        "fixed_version": record.vulnerability_details["lowest_fixed_version"],
                    }
                )

            if package_name in package_details_map.keys():
                package_details_map[package_name]["cves"].sort(key=compare_cve_severity, reverse=True)
                package_details_map[package_name]["current_version"] = package_version
                package_details_map[package_name]["compliant_version"] = calculate_lowest_compliant_version(
                    fix_versions_lists
                )

        cli_outputs.append(
            create_cli_table(
                file_path=file_path,
                cve_count=cve_count,
                package_details_map=package_details_map,
            )
        )

    return "".join(cli_outputs)


def create_cli_table(file_path: str, cve_count: CveCount, package_details_map: Dict[str, Dict[str, Any]]) -> str:
    columns = 6
    table_width = 120
    column_width = int(120 / columns)

    cve_table_lines = create_cve_summary_table_part(
        table_width=table_width, column_width=column_width, cve_count=cve_count
    )

    vulnerable_packages = True if package_details_map else False
    fixable_table_lines = create_fixable_cve_summary_table_part(
        table_width=table_width, column_count=columns, cve_count=cve_count, vulnerable_packages=vulnerable_packages
    )

    package_table_lines = create_package_overview_table_part(
        table_width=table_width, column_width=column_width, package_details_map=package_details_map
    )

    return (
        f"\t{file_path}\n"
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
        cve_table_lines[-1]
        .replace(cve_table.bottom_left_junction_char, cve_table.left_junction_char)
        .replace(cve_table.bottom_right_junction_char, cve_table.right_junction_char)
    )
    cve_table_lines[-1] = cve_table_bottom_line

    return cve_table_lines


def create_fixable_cve_summary_table_part(
    table_width: int, column_count: int, cve_count: CveCount, vulnerable_packages: bool
) -> List[str]:
    fixable_table = PrettyTable(
        header=False, min_table_width=table_width + column_count * 2, max_table_width=table_width + column_count * 2
    )
    fixable_table.set_style(SINGLE_BORDER)
    if cve_count.fixable:
        fixable_table.add_row([f"To fix {cve_count.has_fix}/{cve_count.to_fix} CVEs, go to https://www.bridgecrew.cloud/"])
        fixable_table.align = "l"

    # hack to make multiple tables look like one
    fixable_table_lines = [f"\t{line}" for line in fixable_table.get_string().splitlines(keepends=True)]
    del fixable_table_lines[0]
    # only remove the last line, if there are vulnerable packages
    if vulnerable_packages:
        del fixable_table_lines[-1]

    return fixable_table_lines


def create_package_overview_table_part(
    table_width: int, column_width: int, package_details_map: Dict[str, Dict[str, Any]]
) -> List[str]:
    package_table_lines: List[str] = []
    package_table = PrettyTable(min_table_width=table_width, max_table_width=table_width)
    package_table.set_style(SINGLE_BORDER)
    package_table.field_names = [
        "Package",
        "CVE ID",
        "Severity",
        "Current version",
        "Fixed version",
        "Compliant version",
    ]
    for package_idx, (package_name, details) in enumerate(package_details_map.items()):
        if package_idx > 0:
            del package_table_lines[-1]
            package_table.header = False
            package_table.clear_rows()

        for cve_idx, cve in enumerate(details["cves"]):
            col_package = ""
            col_current_version = ""
            col_compliant_version = ""
            if cve_idx == 0:
                col_package = package_name
                col_current_version = details["current_version"]
                col_compliant_version = details["compliant_version"]

            package_table.add_row(
                [
                    col_package,
                    cve["id"],
                    cve["severity"],
                    col_current_version,
                    cve["fixed_version"],
                    col_compliant_version,
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

    return package_table_lines


async def _report_results_to_bridgecrew_async(
    scan_results: "Iterable[Dict[str, Any]]",
    bc_integration: BcPlatformIntegration,
    bc_api_key: str
) -> "Sequence[int]":
    package_scanning_int = PackageScanningIntegration()
    args = [
        (result, bc_integration, bc_api_key, Path(result["repository"]))
        for result in scan_results
    ]

    if os.getenv("PYCHARM_HOSTED") == "1":
        # PYCHARM_HOSTED env variable equals 1 when running via Pycharm.
        # it avoids us from crashing, which happens when using multiprocessing via Pycharm's debug-mode
        logging.warning("reporting the results in sequence for avoiding crashing when running via Pycharm")
        exit_codes = []
        for curr_arg in args:
            exit_codes.append(await package_scanning_int.report_results_async(*curr_arg))
    else:
        async with Pool() as pool:
            exit_codes = await pool.starmap(package_scanning_int.report_results_async, args)

    return exit_codes


def report_results_to_bridgecrew(
    scan_results: "Iterable[Dict[str, Any]]",
    bc_integration: BcPlatformIntegration,
    bc_api_key: str
) -> "Sequence[int]":
    return asyncio.run(_report_results_to_bridgecrew_async(scan_results, bc_integration, bc_api_key))
