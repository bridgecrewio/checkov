import json

from colorama import init
from junit_xml import TestCase, TestSuite
from termcolor import colored

from checkov.terraform.models.enums import CheckResult

init(autoreset=True)


class Report:
    passed_checks = []
    failed_checks = []
    suppressed_checks = []
    parsing_errors = []

    def add_parsing_errors(self, files):
        for file in files:
            self.add_parsing_error(file)

    def add_parsing_error(self, file):
        if file:
            self.parsing_errors.append(file)

    def add_record(self, record):
        if record.check_result == CheckResult.SUCCESS:
            self.passed_checks.append(record)
        if record.check_result == CheckResult.FAILURE:
            self.failed_checks.append(record)
        if record.check_result == CheckResult.SUPPRESSED:
            self.suppressed_checks.append(record)

    def get_summary(self):
        return {
            "passed": len(self.passed_checks),
            "failed": len(self.failed_checks),
            "suppressed": len(self.suppressed_checks),
            "parsing_errors": len(self.parsing_errors)
        }

    def get_json(self):
        return json.dumps(self.get_dict(), indent=4)

    def get_dict(self):
        return {
            "results": {
                "passed_checks": [check.__dict__ for check in self.passed_checks],
                "failed_checks": [check.__dict__ for check in self.failed_checks],
                "suppressed_checks": [check.__dict__ for check in self.suppressed_checks],
                "parsing_errors": [check.__dict__ for check in self.parsing_errors]
            },
            "summary": self.get_summary()
        }

    def print_console(self):
        summary = self.get_summary()

        if self.parsing_errors:
            message = "\nPassed Checks: {}, Failed Checks: {}, Suppressed Checks: {}, Parsing Errors: {}\n".format(
                summary["passed"], summary["failed"], summary["suppressed"], summary["parsing_errors"])
        else:
            message = "\nPassed Checks: {}, Failed Checks: {}, Suppressed Checks: {}\n".format(
                summary["passed"], summary["failed"], summary["suppressed"])
        print(colored(message, "cyan"))

        for record in self.passed_checks:
            print(record)
        for record in self.failed_checks:
            print(record)

    def print_junit_xml(self):
        ts = self.get_test_suites()
        print(TestSuite.to_xml_string(ts))

    def get_test_suites(self):
        test_cases = {}
        test_suites = []
        records = self.passed_checks + self.failed_checks
        for record in records:
            check_name = record['check_name']
            if check_name not in test_cases:
                test_cases[check_name] = []

            test_name = "{} {}".format(check_name, record['resource'])
            test_case = TestCase(name=test_name, file=record['file_path'], classname=record["check_class"])
            if record['check_result'] == CheckResult.FAILURE:
                test_case.add_failure_info(
                    "Resource \"{}\" failed in check \"{}\"".format(record['resource'], check_name))
            test_cases[check_name].append(test_case)
        for key in test_cases.keys():
            test_suites.append(
                TestSuite(name=key, test_cases=test_cases[key], package=test_cases[key][0].classname))
        return test_suites

    def print_json(self):
        print(self.get_json())
