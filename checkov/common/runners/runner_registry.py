import json
import logging
from abc import abstractmethod

from checkov.common.output.report import Report

OUTPUT_CHOICES = ['cli', 'json', 'junitxml', 'github_failed_only']

from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration


class RunnerRegistry(object):
    runners = []
    scan_reports = []
    banner = ""

    def __init__(self, banner, runner_filter, *runners):
        self.logger = logging.getLogger(__name__)
        self.runner_filter = runner_filter
        self.runners = runners
        self.banner = banner
        self.scan_reports = []
        self.filter_runner_framework()
        self.bc_platform = BcPlatformIntegration()

    @abstractmethod
    def extract_entity_details(self, entity):
        raise NotImplementedError()

    def run(self, root_folder=None, external_checks_dir=None, files=None, guidelines=None, collect_skip_comments=True):
        for runner in self.runners:
            scan_report = runner.run(root_folder, external_checks_dir=external_checks_dir, files=files,
                                     runner_filter=self.runner_filter, collect_skip_comments=collect_skip_comments)
            if guidelines:
                RunnerRegistry.enrich_report_with_guidelines(scan_report, guidelines)
            self.scan_reports.append(scan_report)
        return self.scan_reports

    def print_reports(self, scan_reports, args):
        if args.output == 'cli':
            print(f"{self.banner}\n")
        exit_codes = []
        report_jsons = []
        junit_reports = []
        for report in scan_reports:
            if not report.is_empty():
                if args.output == "json":
                    report_jsons.append(report.get_dict())
                elif args.output == "junitxml":
                    junit_reports.append(report)
                    # report.print_junit_xml()
                elif args.output == 'github_failed_only':
                    report.print_failed_github_md()
                else:
                    report.print_console(is_quiet=args.quiet)
            exit_codes.append(report.get_exit_code(args.soft_fail))
        if args.output == "junitxml":
            if len(junit_reports) == 1:
                junit_reports[0].print_junit_xml()
            else:
                master_report = Report(None)
                for report in junit_reports:
                    master_report.skipped_checks += report.skipped_checks
                    master_report.passed_checks += report.passed_checks
                    master_report.failed_checks += report.failed_checks
                master_report.print_junit_xml()
        if args.output == "json":
            if len(report_jsons) == 1:
                print(json.dumps(report_jsons[0], indent=4))
            else:
                print(json.dumps(report_jsons, indent=4))
        if args.output == "cli":
            self.bc_platform.get_report_to_platform(args,scan_reports)

        exit_code = 1 if 1 in exit_codes else 0
        exit(exit_code)

    def filter_runner_framework(self):
        if not self.runner_filter:
            return
        if self.runner_filter.framework == 'all':
            return
        for runner in self.runners:
            if runner.check_type == self.runner_filter.framework:
                self.runners = [runner]
                return

    @staticmethod
    def enrich_report_with_guidelines(scan_report, guidelines):
        for record in scan_report.failed_checks + scan_report.passed_checks + scan_report.skipped_checks:
            if record.check_id in guidelines:
                record.set_guideline(guidelines[record.check_id])
