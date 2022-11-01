from __future__ import annotations

import argparse
import json
import logging
import os
from collections.abc import Iterable

from typing import List, Dict, Union, Any, Optional, TYPE_CHECKING
from colorama import init
from junit_xml import TestCase, TestSuite, to_xml_report_string
from tabulate import tabulate
from termcolor import colored

from checkov.common.bridgecrew.severities import BcSeverities
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult
from checkov.common.typing import _ExitCodeThresholds
from checkov.common.output.record import Record, SCA_PACKAGE_SCAN_CHECK_NAME
from checkov.common.util.consts import PARSE_ERROR_FAIL_FLAG
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.output import create_cli_output
from checkov.version import version

if TYPE_CHECKING:
    from checkov.common.output.baseline import Baseline
    from checkov.common.output.extra_resource import ExtraResource

init(autoreset=True)

SEVERITY_TO_SARIF_LEVEL = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "none": "none",
}


class Report:
    def __init__(self, check_type: str):
        self.check_type = check_type
        self.passed_checks: list[Record] = []
        self.failed_checks: list[Record] = []
        self.skipped_checks: list[Record] = []
        self.parsing_errors: list[str] = []
        self.resources: set[str] = set()
        self.extra_resources: set[ExtraResource] = set()
        self.image_cached_results: List[dict[str, Any]] = []

    def add_parsing_errors(self, errors: "Iterable[str]") -> None:
        for file in errors:
            self.add_parsing_error(file)

    def add_parsing_error(self, file: str) -> None:
        if file:
            self.parsing_errors.append(file)

    def add_resource(self, resource: str) -> None:
        self.resources.add(resource)

    def add_record(self, record: Record) -> None:
        if record.check_result["result"] == CheckResult.PASSED:
            self.passed_checks.append(record)
        if record.check_result["result"] == CheckResult.FAILED:
            self.failed_checks.append(record)
        if record.check_result["result"] == CheckResult.SKIPPED:
            self.skipped_checks.append(record)

    def get_summary(self) -> Dict[str, Union[int, str]]:
        return {
            "passed": len(self.passed_checks),
            "failed": len(self.failed_checks),
            "skipped": len(self.skipped_checks),
            "parsing_errors": len(self.parsing_errors),
            "resource_count": len(self.resources),
            "checkov_version": version,
        }

    def get_json(self) -> str:
        return json.dumps(self.get_dict(), indent=4, cls=CustomJSONEncoder)

    def get_all_records(self) -> List[Record]:
        return self.failed_checks + self.passed_checks + self.skipped_checks

    def get_dict(self, is_quiet: bool = False, url: str | None = None, full_report: bool = False) -> dict[str, Any]:
        if not url:
            url = "Add an api key '--bc-api-key <api-key>' to see more detailed insights via https://bridgecrew.cloud"
        if is_quiet:
            return {
                "check_type": self.check_type,
                "results": {
                    "failed_checks": [check.__dict__ for check in self.failed_checks]
                },
                "summary": self.get_summary(),
            }
        else:
            return {
                "check_type": self.check_type,
                "results": {
                    "passed_checks": [check.__dict__ for check in self.passed_checks],
                    "failed_checks": [check.__dict__ for check in self.failed_checks],
                    "skipped_checks": [check.__dict__ for check in self.skipped_checks],
                    "parsing_errors": list(self.parsing_errors),
                },
                "summary": self.get_summary(),
                "url": url,
            }

    def get_exit_code(self, exit_code_thresholds: _ExitCodeThresholds) -> int:
        """
        Returns the appropriate exit code depending on the flags that are passed in.

        :return: Exit code 0 or 1.
        """

        hard_fail_on_parsing_errors = os.getenv(PARSE_ERROR_FAIL_FLAG, "false").lower() == 'true'
        logging.debug(f'In get_exit_code; exit code thresholds: {exit_code_thresholds}, hard_fail_on_parsing_errors: {hard_fail_on_parsing_errors}')

        soft_fail_on_checks = exit_code_thresholds['soft_fail_checks']
        soft_fail_threshold = exit_code_thresholds['soft_fail_threshold']
        hard_fail_on_checks = exit_code_thresholds['hard_fail_checks']
        hard_fail_threshold = exit_code_thresholds['hard_fail_threshold']
        soft_fail = exit_code_thresholds['soft_fail']

        has_soft_fail_values = soft_fail_on_checks or soft_fail_threshold
        has_hard_fail_values = hard_fail_on_checks or hard_fail_threshold

        if self.parsing_errors and hard_fail_on_parsing_errors:
            logging.debug('hard_fail_on_parsing_errors is True and there were parsing errors - returning 1')
            return 1
        elif not self.failed_checks or (not has_soft_fail_values and not has_hard_fail_values and soft_fail):
            logging.debug('No failed checks, or soft_fail is True and soft_fail_on and hard_fail_on are empty - returning 0')
            return 0
        elif not has_soft_fail_values and not has_hard_fail_values and self.failed_checks:
            logging.debug('There are failed checks and all soft/hard fail args are empty - returning 1')
            return 1

        for failed_check in self.failed_checks:
            check_id = failed_check.check_id
            bc_check_id = failed_check.bc_check_id
            severity = failed_check.severity

            soft_fail_severity = severity and soft_fail_threshold and severity.level <= soft_fail_threshold.level
            hard_fail_severity = severity and hard_fail_threshold and severity.level >= hard_fail_threshold.level
            explicit_soft_fail = RunnerFilter.check_matches(check_id, bc_check_id, soft_fail_on_checks)
            explicit_hard_fail = RunnerFilter.check_matches(check_id, bc_check_id, hard_fail_on_checks)
            implicit_soft_fail = not explicit_hard_fail and not soft_fail_on_checks and not soft_fail_threshold
            implicit_hard_fail = not explicit_soft_fail and not soft_fail_severity

            if explicit_hard_fail or \
                    (hard_fail_severity and not explicit_soft_fail) or \
                    (implicit_hard_fail and not implicit_soft_fail and not soft_fail):
                logging.debug(f'Check {check_id} (BC ID: {bc_check_id}, severity: {severity.level if severity else None} triggered hard fail - returning 1')
                return 1

        logging.debug('No failed check triggered hard fail - returning 0')
        return 0

    def is_empty(self, full: bool = False) -> bool:
        checks_count = (
            len(self.passed_checks)
            + len(self.failed_checks)
            + len(self.skipped_checks)
            + len(self.parsing_errors)
        )

        if full:
            checks_count += len(self.resources) + len(self.extra_resources) + len(self.image_cached_results)

        return checks_count == 0

    def print_console(
        self,
        is_quiet: bool = False,
        is_compact: bool = False,
        created_baseline_path: str | None = None,
        baseline: Baseline | None = None,
        use_bc_ids: bool = False,
        summary_position: str = 'top'
    ) -> str:
        summary = self.get_summary()
        output_data = colored(f"{self.check_type} scan results:\n", "blue")
        if self.parsing_errors:
            message = "\nPassed checks: {}, Failed checks: {}, Skipped checks: {}, Parsing errors: {}\n\n".format(
                summary["passed"],
                summary["failed"],
                summary["skipped"],
                summary["parsing_errors"],
            )
        else:
            if self.check_type == CheckType.SCA_PACKAGE:
                message = f"\nFailed checks: {summary['failed']}, Skipped checks: {summary['skipped']}\n\n"
            else:
                message = f"\nPassed checks: {summary['passed']}, Failed checks: {summary['failed']}, Skipped checks: {summary['skipped']}\n\n"
        if summary_position == 'top':
            output_data += colored(message, "cyan")
        # output for vulnerabilities is different
        if self.check_type in (CheckType.SCA_PACKAGE, CheckType.SCA_IMAGE):
            if self.failed_checks or self.skipped_checks:
                output_data += create_cli_output(self.check_type == CheckType.SCA_PACKAGE, self.failed_checks, self.skipped_checks)
        else:
            if not is_quiet:
                for record in self.passed_checks:
                    output_data += record.to_string(compact=is_compact, use_bc_ids=use_bc_ids)
            for record in self.failed_checks:
                output_data += record.to_string(compact=is_compact, use_bc_ids=use_bc_ids)
            if not is_quiet:
                for record in self.skipped_checks:
                    output_data += record.to_string(compact=is_compact, use_bc_ids=use_bc_ids)

        if not is_quiet:
            for file in self.parsing_errors:
                output_data += colored(f"Error parsing file {file}ֿ\n", "red")

        if created_baseline_path:
            output_data += colored(
                f"Created a checkov baseline file at {created_baseline_path}",
                "blue",
            )
        if baseline:
            output_data += colored(
                f"Baseline analysis report using {baseline.path} - only new failed checks with respect to the baseline are reported",
                "blue",
            )
        if summary_position == 'bottom':
            output_data += colored(message, "cyan")
        return output_data

    @staticmethod
    def _print_parsing_error_console(file: str) -> None:
        print(colored(f"Error parsing file {file}", "red"))

    def get_sarif_json(self, tool: str) -> Dict[str, Any]:
        runs = []
        rules = []
        results = []
        ruleset = set()
        idx = 0
        level = "warning"
        tool = tool if tool else "Bridgecrew"
        information_uri = "https://docs.bridgecrew.io" if tool.lower() == "bridgecrew" else "https://checkov.io"

        for record in self.failed_checks + self.skipped_checks:
            if self.check_type == CheckType.SCA_PACKAGE and record.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                continue

            help_uri = record.guideline
            if record.vulnerability_details:
                # use the CVE link, if it is a SCA record
                help_uri = record.vulnerability_details.get("link")

            rule = {
                "id": record.check_id,
                "name": record.check_name,
                "shortDescription": {
                    "text": record.short_description if record.short_description else record.check_name,
                },
                "fullDescription": {
                    "text": record.description if record.description else record.check_name,
                },
                "help": {
                    "text": f'"{record.check_name}\nResource: {record.resource}"',
                },
                "defaultConfiguration": {"level": "error"},
            }
            if help_uri:
                rule["helpUri"] = help_uri

            if record.check_id not in ruleset:
                ruleset.add(record.check_id)
                rules.append(rule)
                idx = rules.index(rule)
            else:
                for r in rules:
                    if r['id'] == rule['id']:
                        idx = rules.index(r)
                        break
            if record.file_line_range[0] == 0:
                record.file_line_range[0] = 1
            if record.file_line_range[1] == 0:
                record.file_line_range[1] = 1

            if record.severity:
                level = SEVERITY_TO_SARIF_LEVEL.get(record.severity.name.lower(), "none")
            elif record.check_result.get("result") == CheckResult.FAILED:
                level = "error"

            result = {
                "ruleId": record.check_id,
                "ruleIndex": idx,
                "level": level,
                "attachments": [{'description': detail} for detail in record.details],
                "message": {
                    "text": record.description if record.description else record.check_name,
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": record.file_path.lstrip("/")},
                            "region": {
                                "startLine": int(record.file_line_range[0]),
                                "endLine": int(record.file_line_range[1]),
                            },
                        }
                    }
                ],
            }

            if record.check_result.get("result") == CheckResult.SKIPPED:
                # sca_package suppressions can only be enabled via flag
                # other runners only report in source suppressions
                kind = "external" if record.vulnerability_details else "inSource"
                justification = record.check_result.get("suppress_comment")
                if justification is None:
                    justification = "No comment provided"

                result["suppressions"] = [
                    {
                        "kind": kind,
                        "justification": justification,
                    }
                ]

            results.append(result)

        runs.append({
            "tool": {
                "driver": {
                    "name": tool,
                    "version": version,
                    "informationUri": information_uri,
                    "rules": rules,
                    "organization": "bridgecrew",
                }
            },
            "results": results,
        })
        sarif_template_report = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": runs,
        }
        return sarif_template_report

    def write_sarif_output(self, tool: str) -> None:
        try:
            with open("results.sarif", "w") as f:
                f.write(json.dumps(self.get_sarif_json(tool)))
                print("\nWrote output in SARIF format to the file 'results.sarif'")
        except EnvironmentError as e:
            print("\nAn error occurred while writing SARIF results to file: results.sarif")
            print(f"More details: \n {e}")

    @staticmethod
    def get_junit_xml_string(ts: list[TestSuite]) -> str:
        return to_xml_report_string(ts)

    def print_failed_github_md(self, use_bc_ids: bool = False) -> str:
        result = []
        for record in self.failed_checks:
            result.append(
                [
                    record.get_output_id(use_bc_ids),
                    record.file_path,
                    record.resource,
                    record.check_name,
                    record.guideline,
                ]
            )
        if result:
            table = tabulate(
                result,
                headers=["check_id", "file", "resource", "check_name", "guideline"],
                tablefmt="github",
                showindex=True,
            )
            output_data = f"### {self.check_type} scan results:\n\n{table}\n\n---\n"
            return output_data
        else:
            return "\n\n---\n\n"

    def get_test_suite(self, properties: Optional[Dict[str, Any]] = None, use_bc_ids: bool = False) -> TestSuite:
        """Creates a test suite for the JUnit XML report"""

        test_cases = []

        records = self.passed_checks + self.failed_checks + self.skipped_checks
        for record in records:
            severity = BcSeverities.NONE
            if record.severity:
                severity = record.severity.name

            if self.check_type == CheckType.SCA_PACKAGE:
                if record.check_name != SCA_PACKAGE_SCAN_CHECK_NAME:
                    continue
                if not record.vulnerability_details:
                    # this shouldn't normally happen
                    logging.warning(f"Vulnerability check without details {record.file_path}")
                    continue

                check_id = record.vulnerability_details["id"]
                test_name_detail = f"{record.vulnerability_details['package_name']}: {record.vulnerability_details['package_version']}"
                class_name = f"{record.file_path}.{record.vulnerability_details['package_name']}"
            else:
                check_id = record.bc_check_id if use_bc_ids else record.check_id
                test_name_detail = record.check_name
                class_name = f"{record.file_path}.{record.resource}"

            test_name = f"[{severity}][{check_id}] {test_name_detail}"

            test_case = TestCase(name=test_name, file=record.file_path, classname=class_name)
            if record.check_result["result"] == CheckResult.FAILED:
                test_case.add_failure_info(
                    message=record.check_name,
                    output=self._create_test_case_failure_output(record)
                )
            if record.check_result["result"] == CheckResult.SKIPPED:
                if self.check_type == CheckType.SCA_PACKAGE:
                    test_case.add_skipped_info(f"{check_id} skipped for {test_name_detail}")
                else:
                    test_case.add_skipped_info(record.check_result["suppress_comment"])

            test_cases.append(test_case)

        test_suite = TestSuite(name=f"{self.check_type} scan", test_cases=test_cases, properties=properties)
        return test_suite

    @staticmethod
    def create_test_suite_properties_block(config: argparse.Namespace) -> Dict[str, Any]:
        """Creates a dictionary without 'None' values for the JUnit XML properties block"""

        properties = {k: v for k, v in config.__dict__.items() if v is not None}
        return properties

    def _create_test_case_failure_output(self, record: Record) -> str:
        """Creates the failure output for a JUnit XML test case

        IaC example:
            Resource: azurerm_network_security_rule.fail_rdp
            File: /main.tf: 71-83
            Guideline: https://docs.bridgecrew.io/docs/bc_azr_networking_2

                    71 | resource "azurerm_network_security_rule" "fail_rdp" {
                    72 |   resource_group_name = azurerm_resource_group.example.name
                    73 |   network_security_group_name=azurerm_network_security_group.example_rdp.name
                    74 |   name                       = "fail_security_rule"
                    75 |   direction                  = "Inbound"
                    76 |   access                     = "Allow"
                    77 |   protocol                   = "TCP"
                    78 |   source_port_range          = "*"
                    79 |   destination_port_range     = "3389"
                    80 |   source_address_prefix      = "*"
                    81 |   destination_address_prefix = "*"
                    82 |   priority = 120
                    83 | }

        SCA example:
            Description: Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover.
            Link: https://nvd.nist.gov/vuln/detail/CVE-2019-19844
            Published Date: 2019-12-18T20:15:00+01:00
            Base Score: 9.8
            Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
            Risk Factors: ['Attack complexity: low', 'Attack vector: network', 'Critical severity', 'Has fix']

            Resource: requirements.txt.django
            File: /requirements.txt: 0-0

                    0 | django: 1.2
        """

        failure_output = []

        if self.check_type == CheckType.SCA_PACKAGE:
            if record.vulnerability_details:
                lowest_fixed_version = record.vulnerability_details.get('lowest_fixed_version')
                if lowest_fixed_version is not None:
                    fix = lowest_fixed_version
                else:
                    fixlist = record.vulnerability_details.get('fixed_versions')
                    if fixlist is not None:
                        fix = fixlist

                failure_output.extend(
                    [
                        "",
                        f"Description: {record.description}",
                        f"Link: {record.vulnerability_details.get('link')}",
                        f"Published Date: {record.vulnerability_details.get('published_date')}",
                        f"Base Score: {record.vulnerability_details.get('cvss')}",
                        f"Vector: {record.vulnerability_details.get('vector')}",
                        f"Risk Factors: {record.vulnerability_details.get('risk_factors')}",
                        "Fix Details:",
                        f"  Status: {record.vulnerability_details.get('status')}",
                        f"  Fixed Version: {fix}",
                    ]
                )
            else:
                # this shouldn't normally happen
                logging.warning(f"Vulnerability check without details {record.file_path}")

        failure_output.extend(
            [
                "",
                f"Resource: {record.resource}",
            ]
        )

        if record.file_path:
            file_line = f"File: {record.file_path}"
            if record.file_line_range:
                file_line += f": {record.file_line_range[0]}-{record.file_line_range[1]}"
            failure_output.append(file_line)

        if self.check_type != CheckType.SCA_PACKAGE:
            failure_output.append(f"Guideline: {record.guideline}")

        if record.code_block:
            failure_output.append("")
            failure_output.append(record._code_line_string(code_block=record.code_block, colorized=False))

        return "\n".join(failure_output)

    def print_json(self) -> None:
        print(self.get_json())

    @staticmethod
    def enrich_plan_report(
            report: "Report", enriched_resources: Dict[str, Dict[str, Any]]
    ) -> "Report":
        # This enriches reports with the appropriate filepath, line numbers, and codeblock
        for record in report.failed_checks:
            enriched_resource = enriched_resources.get(record.resource)
            if enriched_resource:
                record.file_path = enriched_resource["scanned_file"]
                record.file_line_range = enriched_resource["entity_lines_range"]
                record.code_block = enriched_resource["entity_code_lines"]
        return report

    @staticmethod
    def handle_skipped_checks(
            report: "Report", enriched_resources: Dict[str, Dict[str, Any]]
    ) -> "Report":
        module_address_len = len("module.")
        skip_records = []
        for record in report.failed_checks:
            resource_skips = enriched_resources.get(record.resource, {}).get(
                "skipped_checks", []
            )
            for skip in resource_skips:
                if record.check_id in skip["id"]:
                    # Mark for removal and add it as a skipped record. It is not safe to remove
                    # the record from failed_checks immediately because we're iterating over it
                    skip_records.append(record)
                    record.check_result["result"] = CheckResult.SKIPPED
                    record.check_result["suppress_comment"] = skip["suppress_comment"]
                    report.add_record(record)

            if record.resource_address and record.resource_address.startswith("module."):
                module_path = record.resource_address[module_address_len:record.resource_address.index('.', module_address_len + 1)]
                module_enrichments = enriched_resources.get(module_path, {})
                for module_skip in module_enrichments.get("skipped_checks", []):
                    if record.check_id in module_skip["id"]:
                        skip_records.append(record)
                        record.check_result["result"] = CheckResult.SKIPPED
                        record.check_result["suppress_comment"] = module_skip["suppress_comment"]
                        report.add_record(record)

        for record in skip_records:
            if record in report.failed_checks:
                report.failed_checks.remove(record)
        return report


def merge_reports(base_report: Report, report_to_merge: Report) -> None:
    base_report.passed_checks.extend(report_to_merge.passed_checks)
    base_report.failed_checks.extend(report_to_merge.failed_checks)
    base_report.skipped_checks.extend(report_to_merge.skipped_checks)
    base_report.parsing_errors.extend(report_to_merge.parsing_errors)
    base_report.image_cached_results.extend(report_to_merge.image_cached_results)
    base_report.resources.update(report_to_merge.resources)
    base_report.extra_resources.update(report_to_merge.extra_resources)


def remove_duplicate_results(report: Report) -> Report:
    def dedupe_records(origin_records: list[Record]) -> list[Record]:
        unique_records: Dict[str, Record] = {}
        for record in origin_records:
            record_hash = record.get_unique_string()
            unique_records[record_hash] = record

        return list(unique_records.values())

    report.passed_checks = dedupe_records(report.passed_checks)
    report.failed_checks = dedupe_records(report.failed_checks)
    return report
