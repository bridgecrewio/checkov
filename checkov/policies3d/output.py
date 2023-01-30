from __future__ import annotations

import itertools
import logging
from collections import defaultdict
from typing import List, Dict, Any

from prettytable import PrettyTable, SINGLE_BORDER
from termcolor import colored

from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.output.record import Record, DEFAULT_SEVERITY


def compare_cve_severity(cve: Dict[str, str]) -> int:
    severity = (cve.get("severity") or DEFAULT_SEVERITY).upper()
    return Severities[severity].level


def create_cli_output( *cve_records: list[Record]) -> str:
    cli_outputs = []

    for record in itertools.chain(*cve_records):
        cli_outputs.append(record.to_string())
        if not record.vulnerabilities:
            #  this shouldn't happen
            logging.error(f"'vulnerabilities' is not set for {record.check_id}")
            continue

        package_cves_details_map: dict[str, dict[str, Any]] = defaultdict(dict)

        for cve in record.vulnerabilities:
            image_name = cve.get('dockerImageName')
            package_name = cve.get('packageName')
            package_version = cve.get('packageVersion')
            severity_str = cve.get('severity', BcSeverities.NONE).lower()

            package_cves_details_map[package_name].setdefault("cves", []).append(
                {
                    "id": cve.get('cveId'),
                    "severity": severity_str
                }
            )

            if package_name in package_cves_details_map:
                package_cves_details_map[package_name]["cves"].sort(key=compare_cve_severity, reverse=True)
                package_cves_details_map[package_name]["current_version"] = package_version
                package_cves_details_map[package_name]["image_name"] = image_name

        if len(package_cves_details_map.keys()):
            cli_outputs.append(
                create_cli_cves_table(
                    file_path=record.file_path,
                    package_details_map=package_cves_details_map,
                )
            )

    return "\n".join(cli_outputs)


def create_cli_cves_table(file_path: str, package_details_map: Dict[str, Dict[str, Any]]) -> str:
    columns = 5
    table_width = 105
    column_width = int(table_width / columns)

    package_table_lines = create_package_overview_table_part(
        table_width=table_width, column_width=column_width, package_details_map=package_details_map
    )

    return colored(
        f"\tRefered Image's Matching CVEs:\n"
        f"{''.join(package_table_lines)}\n",
        'white'
    )


def create_package_overview_table_part(
        table_width: int, column_width: int, package_details_map: Dict[str, Dict[str, Any]]
) -> List[str]:
    package_table_lines: List[str] = []
    package_table = PrettyTable(min_table_width=table_width, max_table_width=table_width)
    package_table.set_style(SINGLE_BORDER)
    package_table.field_names = [
        "Image",
        "Package",
        "CVE ID",
        "Severity",
        "Current version"
    ]
    for package_idx, (package_name, details) in enumerate(package_details_map.items()):
        if package_idx > 0:
            del package_table_lines[-1]
            package_table.header = False
            package_table.clear_rows()

        for cve_idx, cve in enumerate(details["cves"]):
            col_image = ""
            col_package = ""
            col_current_version = ""
            if cve_idx == 0:
                col_image = details["image_name"]
                col_package = package_name
                col_current_version = details["current_version"]

            package_table.add_row(
                [
                    col_image,
                    col_package,
                    cve["id"],
                    cve["severity"],
                    col_current_version
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
