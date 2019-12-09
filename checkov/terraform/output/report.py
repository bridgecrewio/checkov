import json

from colorama import init
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
            self.passed_checks.append(record.__dict__)
        if record.check_result == CheckResult.FAILURE:
            self.failed_checks.append(record.__dict__)
        if record.check_result == CheckResult.SUPPRESSED:
            self.suppressed_checks.append(record.__dict__)

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
                "passed_checks": self.passed_checks,
                "failed_checks": self.failed_checks,
                "suppressed_checks": self.suppressed_checks,
                "parsing_errors": self.parsing_errors
            },
            "summary": self.get_summary()
        }

    def print_console(self):
        report_dict = self.get_dict()
        summary = report_dict["summary"]

        if self.parsing_errors:
            message = "\nPassed Checks: {}, Failed Checks: {}, Suppressed Checks: {}, Parsing Errors: {}\n".format(
                summary["passed"], summary["failed"], summary["suppressed"], summary["parsing_errors"])
        else:
            message = "\nPassed Checks: {}, Failed Checks: {}, Suppressed Checks: {}\n".format(
                summary["passed"], summary["failed"], summary["suppressed"])
        print(colored(message, "cyan"))

        for record in report_dict["results"]["passed_checks"]:
            self.print_record_console(record)
        for record in report_dict["results"]["failed_checks"]:
            self.print_record_console(record)

    @staticmethod
    def print_record_console(record):
        if record['check_result'] == CheckResult.SUCCESS:
            status = "Passed"
            status_color = "green"
        else:
            status = "Failed"
            status_color = "red"
        check_message = colored("Check: \"{}\"\n".format(record["check_name"]), "white")
        file_details = colored("{}:{}\n".format(record["file_path"], record["file_line_range"]), "magenta")
        status_message = colored("\t {} for resource: {} ".format(status, record["resource"]), status_color)
        message = check_message + file_details + status_message
        print(message)

    def print_json(self):
        print(self.get_json())

    # def get_junit_xml(self)
    # def print_junit_xml(self):
