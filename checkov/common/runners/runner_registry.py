import logging
from abc import abstractmethod


class RunnerRegistry(object):
    runners = []
    scan_reports = []
    banner = ""

    def __init__(self,banner, *runners):
        self.logger = logging.getLogger(__name__)
        self.runners = runners
        self.banner = banner

    @abstractmethod
    def extract_entity_details(self, entity):
        raise NotImplementedError()

    def run(self, root_folder, external_checks_dir=None, files=None):
        for runner in self.runners:
            scan_report = runner.run(root_folder, external_checks_dir=external_checks_dir, files=files)
            self.scan_reports.append(scan_report)
        return self.scan_reports

    def print_reports(self,scan_reports, args):
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
