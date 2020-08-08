import json
from collections import defaultdict

from colorama import init
from junit_xml import TestCase, TestSuite
from termcolor import colored

from checkov.common.models.enums import CheckResult
from checkov.version import version
from tabulate import tabulate

init(autoreset=True)


class Report:

    def __init__(self, check_type):
        self.check_type = check_type
        self.passed_checks = []
        self.failed_checks = []
        self.skipped_checks = []
        self.parsing_errors = []

    def add_parsing_errors(self, files):
        for file in files:
            self.add_parsing_error(file)

    def add_parsing_error(self, file):
        if file:
            self.parsing_errors.append(file)

    def add_record(self, record):
        if record.check_result['result'] == CheckResult.PASSED:
            self.passed_checks.append(record)
        if record.check_result['result'] == CheckResult.FAILED:
            self.failed_checks.append(record)
        if record.check_result['result'] == CheckResult.SKIPPED:
            self.skipped_checks.append(record)

    def get_summary(self):
        return {
            "passed": len(self.passed_checks),
            "failed": len(self.failed_checks),
            "skipped": len(self.skipped_checks),
            "parsing_errors": len(self.parsing_errors),
            "checkov_version": version
        }

    def get_json(self):
        return json.dumps(self.get_dict(), indent=4)

    def get_dict(self):
        return {
            "check_type": self.check_type,
            "results": {
                "passed_checks": [check.__dict__ for check in self.passed_checks],
                "failed_checks": [check.__dict__ for check in self.failed_checks],
                "skipped_checks": [check.__dict__ for check in self.skipped_checks],
                "parsing_errors": [check for check in self.parsing_errors]
            },
            "summary": self.get_summary()
        }

    def get_exit_code(self, soft_fail):
        if soft_fail:
            return 0
        elif len(self.failed_checks) > 0:
            return 1
        return 0

    def is_empty(self):
        return len(self.passed_checks) + len(self.failed_checks) + len(self.skipped_checks) == 0

    def print_console(self, is_quiet=False):
        summary = self.get_summary()
        print(colored(f"{self.check_type} scan results:", "blue"))
        if self.parsing_errors:
            message = "\nPassed checks: {}, Failed checks: {}, Skipped checks: {}, Parsing errors: {}\n".format(
                summary["passed"], summary["failed"], summary["skipped"], summary["parsing_errors"])
        else:
            message = "\nPassed checks: {}, Failed checks: {}, Skipped checks: {}\n".format(
                summary["passed"], summary["failed"], summary["skipped"])
        print(colored(message, "cyan"))
        if not is_quiet:
            for record in self.passed_checks:
                print(record)
        for record in self.failed_checks:
            print(record)
        if not is_quiet:
            for record in self.skipped_checks:
                print(record)

    def print_junit_xml(self):
        ts = self.get_test_suites()
        print(TestSuite.to_xml_string(ts))

    def print_failed_github_md(self):
        result = []
        for record in self.failed_checks:
            result.append([record.check_id, record.file_path ,record.resource, record.check_name, record.guideline])
        print(tabulate(result, headers=["check_id", "file" ,"resource", "check_name", "guideline"], tablefmt="github", showindex=True))
        print("\n\n---\n\n")

    def get_test_suites(self):
        test_cases = defaultdict(list)
        test_suites = []
        records = self.passed_checks + self.failed_checks + self.skipped_checks
        for record in records:
            check_name = record.check_name

            test_name = "{} {} {}".format(self.check_type, check_name, record.resource)
            test_case = TestCase(name=test_name, file=record.file_path, classname=record.check_class)
            if record.check_result['result'] == CheckResult.FAILED:
                test_case.add_failure_info(
                    "Resource \"{}\" failed in check \"{}\"".format(record.resource, check_name))
            if record.check_result['result'] == CheckResult.SKIPPED:
                test_case.add_skipped_info(
                    "Resource \"{}\" skipped in check \"{}\"\n Suppress comment: {}".format(record.resource, check_name,
                                                                                            record.check_result[
                                                                                                'suppress_comment']))
            test_cases[check_name].append(test_case)
        for key in test_cases.keys():
            test_suites.append(
                TestSuite(name=key, test_cases=test_cases[key], package=test_cases[key][0].classname))
        return test_suites

    def print_json(self):
        print(self.get_json())

