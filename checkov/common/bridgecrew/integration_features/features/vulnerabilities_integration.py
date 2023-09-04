from __future__ import annotations

import logging
import os
import re
from itertools import groupby
from typing import TYPE_CHECKING, Pattern, Any

from checkov.common.bridgecrew.check_type import CheckType

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import SCA_PACKAGE_SCAN_CHECK_NAME
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.sast.report import SastData, SastReport

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


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
        if not bool(convert_str_to_bool(os.getenv('CKV_ENABLE_UPLOAD_SAST_IMPORTS', False))) or \
                not bool(convert_str_to_bool(os.getenv('CKV_ENABLE_SCA_INTEGRATE_SAST', False))):
            return

        '''
        TODO: 
        1. map CVES by filePath
        2. convert logic of getFilePathByPacakges from TS to Python
        3. move code from step 2 to SAST
        4. write UT
        '''

        # get sast import report for enrich CVEs
        sast_reports = [scan_report for scan_report in merged_reports if type(scan_report) == SastReport]
        if len(sast_reports):
            sast_imports_report = SastData.get_sast_import_report(sast_reports)

        sca_packages_report = [scan_report for scan_report in merged_reports if  scan_report.check_type == CheckType.SCA_PACKAGE]
        if len(sca_packages_report):
            cves_checks = [cve_check for cve_check in sca_packages_report[0].failed_checks if
                                   cve_check.check_name == SCA_PACKAGE_SCAN_CHECK_NAME]
            for cve_check in cves_checks:
                if cve_check.vulnerability_details:
                    file_path = cve_check.file_path
                    package_name = cve_check.vulnerability_details.get('package_name', '')
                    cve_check.vulnerability_details.get('risk_factors', {})['PackageUsed'] = True





integration = VulnerabilitiesIntegration(bc_integration)
