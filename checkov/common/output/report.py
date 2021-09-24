import fnmatch
import json
from collections import defaultdict
from typing import List, Dict, Union, Any, Optional, Set
from colorama import init
from junit_xml import TestCase, TestSuite, to_xml_report_string
from tabulate import tabulate
from termcolor import colored

from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.util.type_forcers import convert_csv_string_arg_to_list
from checkov.version import version

init(autoreset=True)


class Report:
    def __init__(self, check_type: str):
        self.check_type: str = check_type
        self.passed_checks: List[Record] = []
        self.failed_checks: List[Record] = []
        self.skipped_checks: List[Record] = []
        self.parsing_errors: List[str] = []
        self.resources: Set[str] = set()

    def add_parsing_errors(self, errors: List[str]) -> None:
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
        return json.dumps(self.get_dict(), indent=4)

    def get_dict(self, is_quiet=False) -> dict:
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
            }

    def get_exit_code(
        self,
        soft_fail: bool,
        soft_fail_on: Optional[list] = None,
        hard_fail_on: Optional[list] = None,
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
        if soft_fail_on:
            soft_fail_on = convert_csv_string_arg_to_list(soft_fail_on)
            if all(
                any((fnmatch.fnmatch(check_id, pattern) or (bc_check_id and fnmatch.fnmatch(bc_check_id, pattern)))
                    for pattern in soft_fail_on)
                for (check_id, bc_check_id) in (
                    (failed_check.check_id, failed_check.bc_check_id)
                    for failed_check in self.failed_checks
                )
            ):
                # List of "failed checks" is a subset of the "soft fail on" list.
                return 0
            else:
                return 1
        if hard_fail_on:
            hard_fail_on = convert_csv_string_arg_to_list(hard_fail_on)
            if any(
                (check_id in hard_fail_on or bc_check_id in hard_fail_on)
                for (check_id, bc_check_id) in (
                    (failed_check.check_id, failed_check.bc_check_id)
                    for failed_check in self.failed_checks
                )
            ):
                # Any check from the list of "failed checks" is in the list of "hard fail on checks".
                return 1
            else:
                return 0
        if soft_fail:
            return 0
        elif len(self.failed_checks) > 0:
            return 1
        return 0

    def is_empty(self) -> bool:
        return (
            len(self.passed_checks + self.failed_checks + self.skipped_checks)
            + len(self.parsing_errors)
            == 0
        )

    def print_console(
        self,
        is_quiet=False,
        is_compact=False,
        created_baseline_path=None,
        baseline=None,
        use_bc_ids=False,
    ) -> None:
        summary = self.get_summary()
        print(colored(f"{self.check_type} scan results:", "blue"))
        if self.parsing_errors:
            message = "\nPassed checks: {}, Failed checks: {}, Skipped checks: {}, Parsing errors: {}\n".format(
                summary["passed"],
                summary["failed"],
                summary["skipped"],
                summary["parsing_errors"],
            )
        else:
            message = (
                "\nPassed checks: {}, Failed checks: {}, Skipped checks: {}\n".format(
                    summary["passed"], summary["failed"], summary["skipped"]
                )
            )
        print(colored(message, "cyan"))
        if not is_quiet:
            for record in self.passed_checks:
                print(record.to_string(compact=is_compact, use_bc_ids=use_bc_ids))
        for record in self.failed_checks:
            print(record.to_string(compact=is_compact, use_bc_ids=use_bc_ids))
        if not is_quiet:
            for record in self.skipped_checks:
                print(record.to_string(compact=is_compact, use_bc_ids=use_bc_ids))

        if not is_quiet:
            for file in self.parsing_errors:
                Report._print_parsing_error_console(file)

        if created_baseline_path:
            print(
                colored(
                    f"Created a checkov baseline file at {created_baseline_path}",
                    "blue",
                )
            )

        if baseline:
            print(
                colored(
                    f"Baseline analysis report using {baseline.path} - only new failed checks with respect to the baseline are reported",
                    "blue",
                )
            )

    @staticmethod
    def _print_parsing_error_console(file: str) -> None:
        print(colored(f"Error parsing file {file}", "red"))

    def print_junit_xml(self, use_bc_ids: bool = False) -> None:
        ts = self.get_test_suites(use_bc_ids)
        xml_string = self.get_junit_xml_string(ts)
        print(xml_string)

    def get_sarif_json(self) -> Dict[str, Any]:
        runs = []
        rules = []
        results = []
        ruleset = set()
        idx = 0
        for record in self.failed_checks:
            rule = {
                "id": record.check_id,
                "name": record.check_name,
                "shortDescription": {"text": record.check_name},
                "fullDescription": {"text": record.check_name},
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
            result = {
                "ruleId": record.check_id,
                "ruleIndex": idx,
                "level": "error",
                "message": {"text": record.check_name},
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
            results.append(result)

        runs.append({
            "tool": {
                "driver": {
                    "name": "checkov",
                    "version": version,
                    "informationUri": "https://github.com/bridgecrewio/checkov/",
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

    def print_sarif_report(self) -> None:
        print(json.dumps(self.get_sarif_json()))

    @staticmethod
    def get_junit_xml_string(ts: List[TestSuite]) -> str:
        return to_xml_report_string(ts)

    def print_failed_github_md(self, use_bc_ids=False) -> None:
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
        print(
            tabulate(
                result,
                headers=["check_id", "file", "resource", "check_name", "guideline"],
                tablefmt="github",
                showindex=True,
            )
        )
        print("\n\n---\n\n")

    def get_test_suites(self, use_bc_ids=False) -> List[TestSuite]:
        test_cases = defaultdict(list)
        test_suites = []
        records = self.passed_checks + self.failed_checks + self.skipped_checks
        for record in records:
            check_name = f"{record.get_output_id(use_bc_ids)}/{record.check_name}"

            test_name = f"{self.check_type} {check_name} {record.resource}"
            test_case = TestCase(
                name=test_name, file=record.file_path, classname=record.check_class
            )
            if record.check_result["result"] == CheckResult.FAILED:
                if record.file_path and record.file_line_range:
                    test_case.add_failure_info(
                        f"Resource {record.resource} failed in check {check_name} - {record.file_path}:{record.file_line_range} - Guideline: {record.guideline}"
                    )
                else:
                    test_case.add_failure_info(
                        f"Resource {record.resource} failed in check {check_name}"
                    )
            if record.check_result["result"] == CheckResult.SKIPPED:
                test_case.add_skipped_info(
                    f'Resource {record.resource} skipped in check {check_name} \n Suppress comment: {record.check_result["suppress_comment"]} - Guideline: {record.guideline}'
                )

            test_cases[check_name].append(test_case)
        for key in test_cases.keys():
            test_suites.append(
                TestSuite(
                    name=key,
                    test_cases=test_cases[key],
                    package=test_cases[key][0].classname,
                )
            )
        return test_suites

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

        for record in skip_records:
            if record in report.failed_checks:
                report.failed_checks.remove(record)
        return report


def merge_reports(base_report, report_to_merge):
    base_report.passed_checks.extend(report_to_merge.passed_checks)
    base_report.failed_checks.extend(report_to_merge.failed_checks)
    base_report.skipped_checks.extend(report_to_merge.skipped_checks)
    base_report.parsing_errors.extend(report_to_merge.parsing_errors)


def remove_duplicate_results(report):
    def dedupe_records(origin_records):
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
