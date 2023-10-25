from typing import Any, Dict, Union, List, Optional

from checkov.common.output.report import Report
from checkov.sast.consts import POLICIES_ERRORS, POLICIES_ERRORS_COUNT, SOURCE_FILES_COUNT, POLICY_COUNT, SastLanguages


class SastReport(Report):
    def __init__(self, check_type: str, metadata: Dict[str, Optional[Union[str, int, List[str]]]], language: SastLanguages):
        super().__init__(check_type)
        self.metadata = metadata
        self.language: SastLanguages = language
        self.sast_imports: Dict[str, Any] = {}
        self.sast_reachability: Dict[str, Any] = {}

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


class SastData:
    def __init__(self) -> None:
        self.imports_data: Optional[Dict[str, Any]] = None
        self.reachability_report: Optional[Dict[SastLanguages, Any]] = None

    def set_imports_data(self, imports_data: Dict[str, Any]) -> None:
        self.imports_data = imports_data

    def set_reachability_report(self, reachability_report: Dict[SastLanguages, Any]) -> None:
        self.reachability_report = reachability_report

    @staticmethod
    def get_sast_import_report(scan_reports: List[SastReport]) -> Dict[str, Any]:
        sast_imports_report: Dict[SastLanguages, Any] = {}
        for report in scan_reports:
            sast_imports_report[report.language] = {}
        for report in scan_reports:
            for file_name, all_data in report.sast_imports.items():
                current_imports = all_data.get('all', [])
                if current_imports:
                    sast_imports_report[report.language][file_name] = {'all': current_imports}
        return {"imports": sast_imports_report}
