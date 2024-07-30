from typing import Dict, Union, List, Optional

from checkov.common.output.report import Report
from checkov.common.sast.consts import POLICIES_ERRORS, POLICIES_ERRORS_COUNT, SOURCE_FILES_COUNT, POLICY_COUNT, SastLanguages
from checkov.common.sast.report_types import PrismaReport


class CDKReport(Report):
    def __init__(self, check_type: str, metadata: Dict[str, Optional[Union[str, int, List[str]]]], language: SastLanguages, cdk_report: PrismaReport):
        super().__init__(check_type)
        self.metadata = metadata
        self.language: SastLanguages = language
        self.cdk_report: PrismaReport = cdk_report
        # In case we dont have sast report for this lang
        self.empty_sast_report: PrismaReport = PrismaReport(rule_match={language: {}}, profiler={}, errors={}, run_metadata={}, imports={}, reachability_report={}, skipped_checks_by_file={})

    def get_summary(self) -> Dict[str, Union[int, str]]:
        base_summary: Dict[str, Union[int, str]] = super().get_summary()

        err_str = ""
        policies_errors_count = 0
        policies_errors = self.metadata.get(POLICIES_ERRORS)
        if isinstance(policies_errors, list) and policies_errors:
            policies_errors_count = len(policies_errors)
            for e in policies_errors:
                err_str += f"\t- {e}\n"
        base_summary[POLICIES_ERRORS] = err_str
        base_summary[POLICIES_ERRORS_COUNT] = policies_errors_count
        source_files_count = self.metadata.get(SOURCE_FILES_COUNT)
        if isinstance(source_files_count, int) or isinstance(source_files_count, str):
            base_summary[SOURCE_FILES_COUNT] = str(source_files_count)

        policy_count = self.metadata.get(POLICY_COUNT)
        if isinstance(policy_count, int) or isinstance(policy_count, str):
            base_summary[POLICY_COUNT] = policy_count

        return base_summary
