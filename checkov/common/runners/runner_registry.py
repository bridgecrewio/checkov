import logging
from abc import abstractmethod
from functools import reduce
from checkov.common.util.banner import banner
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.terraform.runner import Runner as tf_runner


class RunnerRegistry(object):
    runners = []
    scan_reports = []

    def __init__(self, *runners):
        self.logger = logging.getLogger(__name__)
        self.runners = runners

    @abstractmethod
    def extract_entity_details(self, entity):
        raise NotImplementedError()

    def run(self, root_folder, external_checks_dir=None, files=None):
        for runner in self.runners:
            scan_report = runner().run(root_folder, external_checks_dir=external_checks_dir, files=files)
            self.scan_reports.append(scan_report)
        return self.scan_reports

    @staticmethod
    def print_reports(scan_reports, args):
        print(f"{banner}\n")
        exit_codes = []
        for report in scan_reports:
            if not report.is_empty():
                if args.output == "json":
                    report.print_json()
                elif args.output == "junitxml":
                    report.print_junit_xml()
                else:
                    report.print_console()
            exit_codes.append(report.get_exit_code())
        exit_code = reduce((lambda x, y: x * y), exit_codes)
        exit(exit_code)
