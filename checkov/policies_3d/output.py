from __future__ import annotations

import itertools
import logging
from collections import defaultdict
from typing import List, Dict, Any

from colorama import Style
from prettytable import PrettyTable, SINGLE_BORDER
from termcolor import colored

from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record, DEFAULT_SEVERITY, ANSI_COLORS_DISABLED
from checkov.common.output.common import compare_table_items_severity
from checkov.policies_3d.record import Policy3dRecord

TABLE_WIDTH = 136

def create_iac_code_blocks_output(record: Policy3dRecord) -> str:
    evaluation_message = ""
    suppress_comment = ""

    check_message = colored('Check: {}: "{}"\n'.format(record.get_output_id(use_bc_ids=True), record.check_name),
                            "white")
    guideline_message = ""
    if record.guideline:
        guideline_message = (
                "\tGuide: "
                + Style.BRIGHT
                + colored(f"{record.guideline}\n", "blue", attrs=["underline"])
                + Style.RESET_ALL
        )

    severity_message = f'\tSeverity: {record.severity.name}\n' if record.severity else ''

    resource_blocks = ''
    resource_block_ids = set()

    for iac_record in record.iac_records:
        resource_id = f'{iac_record.file_path}:{iac_record.resource}'
        if resource_id in resource_block_ids:
            # no need to print the same resource block twice
            continue

        resource_details = colored(f'\n\tResource: {iac_record.file_path}:{iac_record.resource}', attrs=['bold'])

        code_lines = ""
        if iac_record.code_block:
            code_lines = "\n{}\n".format(
                "".join([iac_record._code_line_string(iac_record.code_block, not (ANSI_COLORS_DISABLED))]))

        detail = ""
        if iac_record.details:
            detail_buffer = [colored(f"\tDetails: {iac_record.details[0]}\n", "blue")]

            for t in iac_record.details[1:]:
                detail_buffer.append(colored(f"\t         {t}\n", "blue"))

            detail = "".join(detail_buffer)

        caller_file_details = ""
        if iac_record.caller_file_path and iac_record.caller_file_line_range:
            caller_file_details = colored(
                "\tCalling File: {}:{}\n".format(
                    record.caller_file_path, "-".join([str(x) for x in record.caller_file_line_range])
                ),
                "magenta",
            )
        if record.evaluations:
            for (var_name, var_evaluations) in record.evaluations.items():
                var_file = var_evaluations["var_file"]
                var_definitions = var_evaluations["definitions"]
                for definition_obj in var_definitions:
                    definition_expression = definition_obj["definition_expression"]
                    if record._is_expression_in_code_lines(definition_expression):
                        evaluation_message = evaluation_message + colored(
                            f'\tVariable {colored(var_name, "yellow")} (of {var_file}) evaluated to value "{colored(var_evaluations["value"], "yellow")}" '
                            f'in expression: {colored(definition_obj["definition_name"] + " = ", "yellow")}{colored(definition_obj["definition_expression"], "yellow")}\n',
                            "white",
                        )

        resource_blocks += f'{detail}{caller_file_details}{resource_details}{code_lines}{evaluation_message}'
        resource_block_ids.add(resource_id)

    if record.check_result["result"] == CheckResult.FAILED and resource_blocks:
        return f"{check_message}{severity_message}{guideline_message}{resource_blocks}"

    if record.check_result["result"] == CheckResult.SKIPPED:
        return f"{check_message}{severity_message}{suppress_comment}{guideline_message}"
    else:
        return f"{check_message}{severity_message}{evaluation_message}{guideline_message}"


def create_cli_output( *records: list[Policy3dRecord]) -> str:
    cli_outputs = []

    for record in itertools.chain(*records):
        iac_code_blocks_output = create_iac_code_blocks_output(record)
        if iac_code_blocks_output:
            cli_outputs.append(iac_code_blocks_output + Style.RESET_ALL)

        iac_violations_table = render_iac_violations_table(record)
        if iac_violations_table:
            cli_outputs.append(iac_violations_table + Style.RESET_ALL)

        cves_table = render_cve_output(record)
        if cves_table:
            cli_outputs.append(cves_table + Style.RESET_ALL)

        secrets_table = []
        # TODO create a function for creating secrets table, when secrets get into 3d policies
        # Table should have the columns: Secret, Secrety Type, Violation ID, Validation Status (value in red)

    return "\n".join(cli_outputs)


def render_cve_output(record: Policy3dRecord) -> str | None:
    if not record.vulnerabilities:
        #  this shouldn't happen
        logging.error(f"'vulnerabilities' is not set for {record.check_id}")
        return None

    package_cves_details_map: dict[str, dict[str, Any]] = defaultdict(dict)

    for cve in record.vulnerabilities:
        image_name = cve.get('dockerImageName')
        package_name = cve.get('packageName')
        package_version = cve.get('packageVersion')
        severity_str = cve.get('severity', BcSeverities.NONE).upper()

        package_cves_details_map[package_name].setdefault("cves", []).append(
            {
                "id": cve.get('cveId'),
                "severity": severity_str
            }
        )

        if package_name in package_cves_details_map:
            package_cves_details_map[package_name]["cves"].sort(key=compare_table_items_severity, reverse=True)
            package_cves_details_map[package_name]["current_version"] = package_version
            package_cves_details_map[package_name]["image_name"] = image_name

    if len(package_cves_details_map.keys()):
        return (
            create_cli_cves_table(
                file_path=record.file_path,
                package_details_map=package_cves_details_map,
            )
        )

    return None


def create_cli_cves_table(file_path: str, package_details_map: Dict[str, Dict[str, Any]]) -> str:
    columns = 5
    column_width = int(TABLE_WIDTH / columns)

    package_table_lines = create_package_overview_table_part(
        table_width=TABLE_WIDTH, column_width=column_width, package_details_map=package_details_map
    )

    return (
        Style.BRIGHT +
        f"\tImage Referenced with Matching CVEs:\n"
        f"{''.join(package_table_lines)}\n" +
        Style.RESET_ALL
    )


def create_package_overview_table_part(
        table_width: int, column_width: int, package_details_map: Dict[str, Dict[str, Any]]
) -> List[str]:
    package_table_lines: List[str] = []
    package_table = PrettyTable(
        min_table_width=table_width,
        max_table_width=table_width
    )
    package_table.set_style(SINGLE_BORDER)
    package_table.field_names = [
        "Image",
        "Package",
        "Current version",
        "CVE ID",
        "Severity"
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
                    col_current_version,
                    cve["id"],
                    cve["severity"]
                ]
            )

        package_table.align = "l"
        package_table.min_width = column_width
        package_table.max_width = column_width

        for idx, line in enumerate(package_table.get_string().splitlines(keepends=True)):
            if package_idx > 0:
                # hack to make multiple package tables look like one
                line = line.replace(package_table.top_junction_char, package_table.junction_char)
                line = line.replace(package_table.top_left_junction_char, package_table.left_junction_char)
                line = line.replace(package_table.top_right_junction_char, package_table.right_junction_char)


            package_table_lines.append(f"\t{line}")


    return package_table_lines

def render_iac_violations_table(record: Policy3dRecord) -> str | None:
    if not record.iac_records:
        #  this shouldn't happen
        logging.error(f"'iac_records' is not set for {record.check_id}")
        return None

    resource_violation_details_map: dict[str, dict[str, Any]] = defaultdict(dict)

    for iac_record in record.iac_records:
        resource = iac_record.resource
        resource_violation_details_map[resource].setdefault('violations', []).append(
            {
                'id': iac_record.bc_check_id,
                'title': iac_record.check_name,
                'severity': iac_record.severity.name
            }
        )

        if resource in resource_violation_details_map:
            resource_violation_details_map[resource]['violations'].sort(key=compare_table_items_severity, reverse=True)

    if len(resource_violation_details_map.keys()):
        return (
            create_iac_violations_table(
                file_path=record.file_path,
                resource_violation_details_map=resource_violation_details_map,
            )
        )

    return None

def create_iac_violations_table(file_path: str, resource_violation_details_map: Dict[str, Dict[str, Any]]) -> str:
    columns = 5  # it really has only 4 columns, but the title would get a width of two columns
    column_width = int(TABLE_WIDTH / columns)

    iac_table_lines = create_iac_violations_overview_table_part(
        table_width=TABLE_WIDTH, column_width=column_width, resource_violation_details_map=resource_violation_details_map
    )

    return (
        Style.BRIGHT +
        f"\tMatching IaC violations:\n"
        f"{''.join(iac_table_lines)}\n" +
        Style.RESET_ALL
    )


def create_iac_violations_overview_table_part(
        table_width: int, column_width: int, resource_violation_details_map: Dict[str, Dict[str, Any]]
) -> List[str]:
    iac_table_lines: List[str] = []
    iac_table = PrettyTable(
        min_table_width=table_width,
        max_table_width=table_width
    )
    iac_table.set_style(SINGLE_BORDER)
    iac_table.field_names = [
        "Resource",
        "Violation",
        "Title",
        "Severity"
    ]
    for resource_idx, (resource, details) in enumerate(resource_violation_details_map.items()):
        if resource_idx > 0:
            del iac_table_lines[-1]
            iac_table.header = False
            iac_table.clear_rows()

        for violation_idx, violation in enumerate(details['violations']):
            col_resource = ''
            if violation_idx == 0:
                col_resource = resource

            iac_table.add_row(
                [
                    col_resource,
                    violation['id'],
                    violation['title'],
                    violation['severity']
                ]
            )

        iac_table.align = "l"
        # the column widths are manipulated here with -2s so all the printed tables have eventually the same width
        iac_table.min_width = column_width - 2
        iac_table.max_width = column_width - 2
        iac_table.min_width['Title'] = 2 * column_width - 2
        iac_table.max_width['Title'] = 2 * column_width - 2

        for idx, line in enumerate(iac_table.get_string().splitlines(keepends=True)):
            if resource_idx > 0:
                # hack to make multiple package tables look like one
                line = line.replace(iac_table.top_junction_char, iac_table.junction_char)
                line = line.replace(iac_table.top_left_junction_char, iac_table.left_junction_char)
                line = line.replace(iac_table.top_right_junction_char, iac_table.right_junction_char)

            iac_table_lines.append(f"\t{line}")

    return iac_table_lines