import logging
from typing import Any, Dict, Union, List, Optional

from checkov.common.output.report import Report
from checkov.common.sast.consts import POLICIES_ERRORS, POLICIES_ERRORS_COUNT, SOURCE_FILES_COUNT, POLICY_COUNT, SastLanguages
from checkov.common.sast.report_types import PrismaReport


class SastReport(Report):
    def __init__(self, check_type: str, metadata: Dict[str, Optional[Union[str, int, List[str]]]], language: SastLanguages, sast_report: PrismaReport):
        super().__init__(check_type)
        self.metadata = metadata
        self.language: SastLanguages = language
        self.sast_imports: Dict[str, Any] = {}
        self.sast_reachability: Dict[str, Any] = {}
        self.sast_report: PrismaReport = sast_report

    @property
    def errors(self) -> Dict[str, Any]:
        return {k: v for k, v in self.sast_report.errors.items() if isinstance(v, str) and "policy" not in v.lower()}

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

    @staticmethod
    def get_formated_reachability_report(reachability_report_dict: Dict[SastLanguages, Any]) -> Dict[str, Any]:
        formated_report: Dict[str, Any] = {}
        for lang, repos_data in reachability_report_dict.items():
            formated_report[lang.value] = []
            for repo_name, files_data in repos_data.items():
                new_repo = {'Name': repo_name, 'Files': []}
                for file_path, packages_data in files_data['files'].items():
                    new_file = {'Path': file_path, 'Packages': []}
                    for package_name, package_data in packages_data['packages'].items():
                        new_package = {'Name': package_name, 'Alias': package_data['alias'], 'Functions': []}
                        for func in package_data['functions']:
                            new_func = {'Name': func['name'], 'Alias': func['alias'], 'LineNumber': func['line_number'], 'CodeBlock': [func['code_block']], 'CveId': func.get('cve_id', '')}
                            new_package['Functions'].append(new_func)
                        new_file['Packages'].append(new_package)
                    new_repo['Files'].append(new_file)
                formated_report[lang.value].append(new_repo)
        return formated_report


class SastData:
    def __init__(self) -> None:
        self.imports_data: Optional[Dict[str, Any]] = None
        self.reachability_report: Optional[Dict[str, Any]] = None

    def set_imports_data(self, imports_data: Dict[str, Any]) -> None:
        self.imports_data = imports_data

    def set_reachability_report(self, reachability_report: Dict[str, Any]) -> None:
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
                    aliases = all_data.get('aliases', {})
                    sast_imports_report[report.language][file_name]['aliases'] = aliases
        return {"imports": sast_imports_report}

    @staticmethod
    def get_sast_reachability_report(scan_reports: List[SastReport]) -> Dict[str, Any]:
        first_found_repo_name = None
        sast_reachability_report: Dict[SastLanguages, Any] = {}
        for report in scan_reports:
            sast_reachability_report[report.language] = {}
        for report in scan_reports:
            for repo_name, repo_data in report.sast_reachability.items():

                # validating we are dealing only with one repo, as it happens for imports report
                if first_found_repo_name:
                    if repo_name != first_found_repo_name:
                        logging.error(f'[get_sast_reachability_report] - found more than one repository in '
                                      f'the scan reports. {scan_reports}')
                        return {"reachability": {}}
                else:
                    first_found_repo_name = repo_name

                for file_name, file_data in repo_data.files.items():
                    sast_reachability_report[report.language][file_name] = file_data
        return {"reachability": sast_reachability_report}
