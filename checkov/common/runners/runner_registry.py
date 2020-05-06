import logging
from abc import abstractmethod


class RunnerRegistry(object):
    runners = []
    scan_reports = []
    banner = ""

    def __init__(self, banner,runner_filter, *runners):
        self.logger = logging.getLogger(__name__)
        self.runner_filter = runner_filter
        self.runners = runners
        self.banner = banner
        self.filter_runner_framework()

    @abstractmethod
    def extract_entity_details(self, entity):
        raise NotImplementedError()

    def run(self, root_folder=None, external_checks_dir=None, files=None):
        for runner in self.runners:
            scan_report = runner.run(root_folder, external_checks_dir=external_checks_dir, files=files,runner_filter=self.runner_filter)
            self.scan_reports.append(scan_report)
        return self.scan_reports

    def print_reports(self, scan_reports, args):
        if args.output != "json" and args.output != "junitxml":
            print(f"{self.banner}\n")
        exit_codes = []
        for report in scan_reports:
            if not report.is_empty():
                if args.output == "json":
                    report.print_json()
                elif args.output == "junitxml":
                    report.print_junit_xml()
                else:
                    report.print_console()
            exit_codes.append(report.get_exit_code(args.soft_fail))
        exit_code = 1 if 1 in exit_codes else 0
        exit(exit_code)

    def filter_runner_framework(self):
        if self.runner_filter.framework =='all':
            return
        for runner in self.runners:
            if runner.check_type == self.runner_filter.framework:
                self.runners = [runner]
                return
