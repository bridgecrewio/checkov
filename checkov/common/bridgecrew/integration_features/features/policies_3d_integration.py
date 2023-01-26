from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities
from checkov.common.policies3d.checks_parser import Policy3dParser
from checkov.common.util.type_forcers import force_list
from checkov.common.checks_infra.registry import Registry, get_graph_checks_registry

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner


class Policies3DIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=11)
        self.platform_policy_parser = Policy3dParser()

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

    @staticmethod
    def _convert_raw_check(policy: dict[str, Any]) -> dict[str, Any]:
        metadata = {
            'id': policy['id'],
            'name': policy['title'],
            'category': policy['category'],
            'frameworks': policy.get('frameworks', [])
        }
        check = {
            'metadata': metadata,
            'definition': json.loads(policy['code'])
        }
        return check

    def extend_records_with_cloned_policies(self, records: list[Record]) -> list[Record]:
        bc_check_ids = [record.bc_check_id for record in records]
        for idx, bc_check_id in enumerate(bc_check_ids):
            cloned_policies = self.bc_cloned_checks.get(bc_check_id, [])  # type:ignore[arg-type]  # bc_check_id can be None
            logging.debug('Cloned policies to be deep copied:')
            logging.debug(cloned_policies)
            logging.debug('From origin policy:')
            logging.debug(records[idx].get_unique_string())
            for cloned_policy in cloned_policies:
                new_record = deepcopy(records[idx])
                new_record.check_id = cloned_policy['id']
                new_record.bc_check_id = cloned_policy['id']
                new_record.guideline = cloned_policy['guideline']
                new_record.severity = cloned_policy['severity']
                new_record.check_name = cloned_policy['title']
                records.append(new_record)
        return records

    def post_scan(self, scan_reports: list[Report]) -> None:
        # 1. get the 3d policies from self.bc_integration['customer_run_config']['Policies3D']
        try:
            if not self.bc_integration.customer_run_config_response:
                logging.debug('In the post scan for custom policies, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            policies = self.bc_integration.customer_run_config_response.get('Policies3D')
            # 2. for each policy:
            for policy in policies:
                try:
                    logging.debug(f"Loading policy id: {policy.get('id')}")
                    # 2.1 parse it to a 3dCheck
                    # converted_check = self._convert_raw_check(policy)

                    # 2.2 run the check against the scan_reports
                    # 2.3 update the scan_reports with the new findings
                    # resource_types = Registry._get_resource_types(converted_check['metadata'])
                    # check = self.platform_policy_parser.parse_raw_check(converted_check, resources_types=resource_types)
                    # check.severity = Severities[policy['severity']]
                    # check.bc_id = check.id

                    #TODO move this to parser / solver of the policy itself
                    check_result = 'passed'
                    definition = json.loads(policy.get('code'))
                    iac_based = definition.get('iac')
                    cve_based = definition.get('cve')
                    reports_by_fw = {report.check_type: report for report in scan_reports}
                    if cve_based:
                        cve_report = reports_by_fw.get('sca_image')
                        if cve_report:
                            cve_records = cve_report.failed_checks
                            # extract what's need to be checked
                            risk_factor = None
                            for attribute, value in cve_based.items():
                                if attribute == 'risk_factor':
                                    risk_factor = value[0]

                            # get all relevant cve scan reports
                            if risk_factor:
                                cve_records = [record for record in cve_records if risk_factor in force_list(record.vulnerability_details.get('risk_factors', []))]

                    if iac_based:
                        # extract what's need to be checked
                        for fw, bc_check_ids in iac_based.items():
                            fw_report = reports_by_fw.get(fw)
                            if fw_report:
                                fw_records = fw_report.failed_checks
                                fw_records = [record for record in fw_records if record.bc_check_id in bc_check_ids]







                except Exception:
                    logging.debug(f"Failed to load policy id: {policy.get('id')}", exc_info=True)
            logging.debug(f'Found {len(policies)} custom policies from the platform.')
        except Exception:
            self.integration_feature_failures = True
            logging.debug("Scanning without applying custom policies from the platform.", exc_info=True)
        pass


integration = Policies3DIntegration(bc_integration)
