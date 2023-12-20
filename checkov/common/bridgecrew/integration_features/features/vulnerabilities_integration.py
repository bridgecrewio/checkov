from __future__ import annotations

import os
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Tuple, Set

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.output.record import SCA_PACKAGE_SCAN_CHECK_NAME, Record
from checkov.common.sast.consts import SastLanguages
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.sast.report import SastData, SastReport
from checkov.common.sca.consts import get_package_by_str, ScaPackageFile, sca_package_to_sast_lang_map

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner

NORMALIZE_PREFIX = 'BC_NORMALIZE_'


class VulnerabilitiesIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=2)  # must be after the custom policies integration
        # the provider may be lower or upper depending on where the policy was created

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self) -> None:
        # not used
        pass

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass

    def post_runner(self, scan_report: Report) -> None:
        # not used
        pass

    def post_scan(self, merged_reports: list[Report]) -> None:
        self.merge_sca_and_sast_reports(merged_reports)

    def merge_sca_and_sast_reports(self, merged_reports: list[Report]) -> None:
        if not bool(convert_str_to_bool(os.getenv('CKV_ENABLE_UPLOAD_SAST_IMPORTS', False))) or \
                not bool(convert_str_to_bool(os.getenv('CKV_ENABLE_SCA_INTEGRATE_SAST', False))):
            return

        # Extract SAST imports report and reachability report
        sast_reports = [scan_report for scan_report in merged_reports if isinstance(scan_report, SastReport)]
        if not len(sast_reports):
            return

        sast_imports_report = SastData.get_sast_import_report(sast_reports)
        sast_reacability_report = SastData.get_sast_reachability_report(sast_reports)

        # Extract SCA packages report
        sca_packages_report = [scan_report for scan_report in merged_reports if
                               scan_report.check_type == CheckType.SCA_PACKAGE]
        if not len(sca_packages_report):
            return

        # Extract vulnerabilities failed checks
        cves_checks = [cve_check for cve_check in sca_packages_report[0].failed_checks if
                       cve_check.check_name == SCA_PACKAGE_SCAN_CHECK_NAME]

        # Create a dictionary to store the grouped records
        grouped_records = self.group_cves_checks_by_files(cves_checks)

        # Iterate over each file, get sast imports and enrich it's Cves
        for sca_file_path, current_cves in grouped_records.items():

            # Determine the langauge of file
            lang = self.get_sast_lang_by_file_path(sca_file_path)

            # Extract Sast data from Sast report filtered by the language
            imports_entries = sast_imports_report.get('imports', {}).get(lang, {}).items()
            filtered_imports_entries = [(code_file_path, sast_data) for code_file_path, sast_data in imports_entries if
                                        self.is_deeper_or_equal_level(sca_file_path, code_file_path)]

            reachability_entries = sast_reacability_report.get('reachability', {}).get(lang, {}).items()
            filtered_reachability_entries = [(code_file_path, sast_data) for code_file_path, sast_data in
                                             reachability_entries if self.is_deeper_or_equal_level(sca_file_path,
                                                                                                   code_file_path)]

            if not len(filtered_imports_entries) and not len(filtered_reachability_entries):
                continue

            # Create maps with the relevant structure for the enrichment step
            sast_files_by_package_map = self.create_file_by_package_map(filtered_imports_entries)
            sast_reachable_cves_by_package_map = self.create_reachable_cves_by_package_map(filtered_reachability_entries)

            # Enrich the CVEs
            self.enrich_cves_with_sast_data(current_cves, sast_files_by_package_map, sast_reachable_cves_by_package_map)

    '''
    Each SCA report check has file_path, we want to getter same file_path so we won't have to calculate SAST language more then once
    '''

    def group_cves_checks_by_files(self, cves_checks: List[Record]) -> Dict[str, List[Record]]:
        # Create a dictionary to store the grouped records
        grouped_records: Dict[str, List[Record]] = defaultdict()

        # Group the records by the 'file_path' key
        for record in cves_checks:
            file_path = record.file_path
            if file_path not in grouped_records:
                grouped_records[file_path] = list()
            grouped_records[file_path].append(record)

        return grouped_records

    '''
    convert SAST report structure to a sturcture grouped by package_name, for better performance in the enrich step
    '''

    def create_file_by_package_map(self, filtered_entries: List[Tuple[Any, Any]]) -> Dict[str, List[str]]:
        sast_files_by_packages_map: Dict[str, List[str]] = defaultdict(list)
        for code_file_path, sast_data in filtered_entries:
            for package_name in sast_data['all']:
                clean_package_name = package_name.strip("'")

                # in case it is alias-name, getting the real one
                if package_name in sast_data.get('aliases', {}):
                    clean_package_name = sast_data['aliases'][package_name]

                # Normalize package name
                normalize_package_name = self.normalize_package_name(clean_package_name)

                if clean_package_name not in sast_files_by_packages_map:
                    sast_files_by_packages_map[clean_package_name] = list()
                if normalize_package_name not in sast_files_by_packages_map:
                    sast_files_by_packages_map[normalize_package_name] = list()

                sast_files_by_packages_map[clean_package_name].append(code_file_path)
                sast_files_by_packages_map[normalize_package_name].append(code_file_path)

        return sast_files_by_packages_map

    def create_reachable_cves_by_package_map(self, filtered_reachability_entries: List[Tuple[Any, Any]]) -> Dict[str, Set[str]]:
        reachable_cves_by_packages_map: Dict[str, Set[str]] = defaultdict(set)
        for _, file_data in filtered_reachability_entries:
            packages = file_data.packages
            for package_name, package_data in packages.items():
                for function_item in package_data.functions:
                    reachable_cves_by_packages_map[package_name].add(function_item.cve_id)
        return reachable_cves_by_packages_map

#######################################################################################################################
    '''
    enrich each CVE with the risk factor of IsUsed - which means there is a file the use the package of that CVE
    '''

    def _is_package_used_for_cve(self, cve_vulnerability_details: Dict[str, Any], sast_files_by_package_map: Dict[str, List[str]]) -> bool:
        package_name = cve_vulnerability_details.get('package_name', '')
        normalize_package_name = self.normalize_package_name(package_name)
        return package_name in sast_files_by_package_map or normalize_package_name in sast_files_by_package_map

    def _is_reachable_function_for_cve(self, cve_vulnerability_details: Dict[str, Any], sast_reachable_cves_by_package_map: Dict[str, Set[str]]) -> bool:
        package_name = cve_vulnerability_details.get('package_name', '')
        return cve_vulnerability_details.get('id') in sast_reachable_cves_by_package_map.get(package_name, set())

    def enrich_cves_with_sast_data(
            self,
            current_cves: List[Record],
            sast_files_by_package_map: Dict[str, List[str]],
            sast_reachable_cves_by_package_map: Dict[str, Set[str]]
    ) -> None:
        for cve_check in current_cves:
            if cve_check.vulnerability_details:
                is_package_used = self._is_package_used_for_cve(cve_check.vulnerability_details, sast_files_by_package_map)
                cve_check.vulnerability_details.get('risk_factors', {})['IsUsed'] = is_package_used

                is_reachable_function = self._is_reachable_function_for_cve(cve_check.vulnerability_details, sast_reachable_cves_by_package_map)
                cve_check.vulnerability_details.get('risk_factors', {})['ReachableFunction'] = is_reachable_function
#######################################################################################################################

    '''
    we want to consider sast info only on files that are on the same level of the SCA file or deeper.
    '''

    def is_deeper_or_equal_level(self, main_file_path: str, other_file_path: str) -> bool:
        relative_path = os.path.relpath(os.path.dirname(other_file_path), os.path.dirname(main_file_path))
        return not other_file_path.startswith('.') and not relative_path.startswith('..') and not os.path.isabs(
            relative_path)

    '''
    getting file_path of SCA file, like package.json and need to convert it to SAST language like Javascript
    first we are converting the sca file to package file like, and then converting it to SAST language
    '''

    def get_sast_lang_by_file_path(self, file_path: str) -> Optional[SastLanguages]:
        suffix = file_path.split('/').pop() or ''
        sca_package: Optional[ScaPackageFile] = get_package_by_str(suffix)
        if not sca_package:
            return None

        return sca_package_to_sast_lang_map.get(sca_package, None)

    '''
    normalize the package name because there can be different between the package name as it present in the SCA file and
    in the way it used in the code, so we are removing special chars for better comperation
    '''

    def normalize_package_name(self, package_name: str) -> str:
        normalize_package: str = package_name.replace('-', '').replace('_', '')

        if './' in package_name:
            last_index = package_name.rfind('/')
            normalize_package = package_name[last_index + 1:]

        return f"{NORMALIZE_PREFIX}{normalize_package}"


integration = VulnerabilitiesIntegration(bc_integration)
