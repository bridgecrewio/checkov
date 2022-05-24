from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import List, Dict, Union, Any, Optional, Set, TYPE_CHECKING, cast

from colorama import init
from junit_xml import TestCase, TestSuite, to_xml_report_string  # type:ignore[import]
from tabulate import tabulate
from termcolor import colored

from checkov import sca_package
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.common.util.type_forcers import convert_csv_string_arg_to_list
from checkov.runner_filter import RunnerFilter
from checkov.version import version

if TYPE_CHECKING:
    from checkov.common.output.baseline import Baseline

init(autoreset=True)

@dataclass
class CheckType:
    BITBUCKET_PIPELINES = "bitbucket_pipelines"
    ARM = "arm"
    BICEP = "bicep"
    CLOUDFORMATION = "cloudformation"
    DOCKERFILE = "dockerfile"
    GITHUB_CONFIGURATION = "github_configuration"
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CONFIGURATION = "gitlab_configuration"
    GITLAB_CI = "gitlab_ci"
    BITBUCKET_CONFIGURATION = "bitbucket_configuration"
    HELM = "helm"
    JSON = "json"
    YAML = "yaml"
    KUBERNETES = "kubernetes"
    KUSTOMIZE = "kustomize"
    OPENAPI = "openapi"
    SCA_PACKAGE = "sca_package"
    SCA_IMAGE = "sca_image"
    SECRETS = "secrets"
    SERVERLESS = "serverless"
    TERRAFORM = "terraform"
    TERRAFORM_PLAN = "terraform_plan"

SEVERITY_TO_SARIF_LEVEL = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "none": "none",
}


class Report:
    def __init__(self, check_type: str):
        self.check_type: str = check_type
        self.passed_checks: List[Record] = []
        self.failed_checks: List[Record] = []
        self.skipped_checks: List[Record] = []
        self.parsing_errors: List[str] = []
        self.resources: Set[str] = set()

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

    def get_dict(self, is_quiet: bool = False, url: str = "") -> dict[str, Any]:
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

    def get_exit_code(
        self,
        soft_fail: bool,
        soft_fail_on: list[str] | None = None,
        hard_fail_on: list[str] | None = None,
    ) -> int:
        """
        Returns the appropriate exit code depending on the flags that are passed in.

        :param soft_fail: If true, exit code is always 0. (default is false)
        :param soft_fail_on: A list of checks that will return exit code 0 if they fail. Other failing checks will
        result exit code 1.
        :param hard_fail_on: A list of checks that will return exit code 1 if they fail. Other failing checks will
        result exit code 0.
        :return: Exit code 0 or 1.
        """

        logging.debug(f'In get_exit_code; soft_fail: {soft_fail}, soft_fail_on: {soft_fail_on}, hard_fail_on: {hard_fail_on}')

        if not self.failed_checks or (not soft_fail_on and not hard_fail_on and soft_fail):
            logging.debug('No failed checks, or soft_fail is True and soft_fail_on and hard_fail_on are empty - returning 0')
            return 0
        elif not soft_fail_on and not hard_fail_on and self.failed_checks:
            logging.debug('There are failed checks and all soft/hard fail args are empty - returning 1')
            return 1

        soft_fail_on_checks = []
        soft_fail_threshold = None
        # soft fail on the highest severity threshold in the list
        for val in convert_csv_string_arg_to_list(soft_fail_on):
            if val in Severities:
                if not soft_fail_threshold or Severities[val].level > soft_fail_threshold.level:
                    soft_fail_threshold = Severities[val]
            else:
                soft_fail_on_checks.append(val)

        logging.debug(f'Soft fail severity threshold: {soft_fail_threshold.level if soft_fail_threshold else None}')
        logging.debug(f'Soft fail checks: {soft_fail_on_checks}')

        hard_fail_on_checks = []
        hard_fail_threshold = None
        # hard fail on the lowest threshold in the list
        for val in convert_csv_string_arg_to_list(hard_fail_on):
            if val in Severities:
                if not hard_fail_threshold or Severities[val].level < hard_fail_threshold.level:
                    hard_fail_threshold = Severities[val]
            else:
                hard_fail_on_checks.append(val)

        logging.debug(f'Hard fail severity threshold: {hard_fail_threshold.level if hard_fail_threshold else None}')
        logging.debug(f'Hard fail checks: {hard_fail_on_checks}')

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

    def is_empty(self) -> bool:
        return (
            len(self.passed_checks + self.failed_checks + self.skipped_checks)
            + len(self.parsing_errors)
            == 0
        )

    def print_console(
        self,
        is_quiet: bool = False,
        is_compact: bool = False,
        created_baseline_path: str | None = None,
        baseline: Baseline | None = None,
        use_bc_ids: bool = False,
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
                message = f"\nFound CVEs: {summary['failed']}, Skipped CVEs: {summary['skipped']}\n\n"
            else:
                message = f"\nPassed checks: {summary['passed']}, Failed checks: {summary['failed']}, Skipped checks: {summary['skipped']}\n\n"
        output_data += colored(message, "cyan")
        # output for vulnerabilities is different
        if self.check_type in (CheckType.SCA_PACKAGE, CheckType.SCA_IMAGE):
            if self.failed_checks or self.skipped_checks:
                output_data += sca_package.output.create_cli_output(self.check_type == CheckType.SCA_PACKAGE, self.failed_checks, self.skipped_checks)
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
                    "text": f'"{record.check_name}\nResource: {record.resource}\nGuideline: {record.guideline}"',
                },
                "defaultConfiguration": {"level": "error"},
            }
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
    def get_junit_xml_string(ts: List[TestSuite]) -> str:
        return cast(str, to_xml_report_string(ts))

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
        output_data = tabulate(
            result,
            headers=["check_id", "file", "resource", "check_name", "guideline"],
            tablefmt="github",
            showindex=True,
        ) + "\n\n---\n\n"
        print(output_data)
        return output_data

    def get_test_suite(self, properties: Optional[Dict[str, Any]] = None, use_bc_ids: bool = False) -> TestSuite:
        """Creates a test suite for the JUnit XML report"""

        test_cases = []

        records = self.passed_checks + self.failed_checks + self.skipped_checks
        for record in records:
            severity = BcSeverities.NONE
            if record.severity:
                severity = record.severity.name

            if self.check_type == CheckType.SCA_PACKAGE:
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
                failure_output.extend(
                    [
                        "",
                        f"Description: {record.description}",
                        f"Link: {record.vulnerability_details.get('link')}",
                        f"Published Date: {record.vulnerability_details.get('published_date')}",
                        f"Base Score: {record.vulnerability_details.get('cvss')}",
                        f"Vector: {record.vulnerability_details.get('vector')}",
                        f"Risk Factors: {record.vulnerability_details.get('risk_factors')}",
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
                module_path = record.resource_address[0:record.resource_address.index('.', len("module.") + 1)]
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


def remove_duplicate_results(report: Report) -> Report:
    def dedupe_records(origin_records: list[Record]) -> list[Record]:
        record_cache = []
        new_records = []
        for record in origin_records:
            record_hash = record.get_unique_string()
            if record_hash not in record_cache:
                new_records.append(record)
                record_cache.append(record_hash)
        return new_records

    report.passed_checks = dedupe_records(report.passed_checks)
    report.failed_checks = dedupe_records(report.failed_checks)
    return report
