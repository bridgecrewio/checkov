from __future__ import annotations

import json
import logging
import re
from collections import defaultdict
from copy import deepcopy
from typing import TYPE_CHECKING, Any, List

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities
from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry, get_graph_checks_registry

if TYPE_CHECKING:
    from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
    from checkov.common.output.record import Record
    from checkov.common.output.report import Report
    from checkov.common.typing import _BaseRunner

# service-provider::service-name::data-type-name
CFN_RESOURCE_TYPE_IDENTIFIER = re.compile(r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$")


class CustomPoliciesIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration: BcPlatformIntegration) -> None:
        super().__init__(bc_integration=bc_integration, order=1)  # must be after policy metadata and before suppression integration
        self.platform_policy_parser = GraphCheckParser()
        self.policies_url = f"{self.bc_integration.api_url}/api/v1/policies/table/data"
        self.bc_cloned_checks: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.policy_level_suppression: List[str] = []

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_download
            and not self.integration_feature_failures
        )

    def pre_scan(self) -> None:
        try:
            if not self.bc_integration.customer_run_config_response:
                logging.debug('In the pre-scan for custom policies, but nothing was fetched from the platform')
                self.integration_feature_failures = True
                return

            policies = self.bc_integration.customer_run_config_response.get('customPolicies')
            for policy in policies:
                try:
                    logging.debug(f"Loading policy id: {policy.get('id')}")
                    converted_check = self._convert_raw_check(policy)
                    source_incident_id = policy.get('sourceIncidentId')
                    if source_incident_id:
                        policy['severity'] = Severities[policy['severity']]
                        self.bc_cloned_checks[source_incident_id].append(policy)
                        continue
                    resource_types = Registry._get_resource_types(converted_check['metadata'])
                    check = self.platform_policy_parser.parse_raw_check(converted_check, resources_types=resource_types)
                    check.severity = Severities[policy['severity']]
                    check.bc_id = check.id
                    if check.frameworks:
                        for f in check.frameworks:
                            if f.lower() == "cloudformation":
                                get_graph_checks_registry("cloudformation").checks.append(check)
                            elif f.lower() == "terraform":
                                get_graph_checks_registry("terraform").checks.append(check)
                            elif f.lower() == "kubernetes":
                                get_graph_checks_registry("kubernetes").checks.append(check)
                    elif re.match(CFN_RESOURCE_TYPE_IDENTIFIER, check.resource_types[0]):
                        get_graph_checks_registry("cloudformation").checks.append(check)
                    else:
                        get_graph_checks_registry("terraform").checks.append(check)
                except Exception:
                    logging.debug(f"Failed to load policy id: {policy.get('id')}", exc_info=True)
            logging.debug(f'Found {len(policies)} custom policies from the platform.')
        except Exception:
            self.integration_feature_failures = True
            logging.debug("Scanning without applying custom policies from the platform.", exc_info=True)

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

    def post_runner(self, scan_report: Report) -> None:
        if self.bc_cloned_checks:
            scan_report.failed_checks = self.extend_records_with_cloned_policies(scan_report.failed_checks)
            scan_report.passed_checks = self.extend_records_with_cloned_policies(scan_report.passed_checks)
            scan_report.skipped_checks = self.extend_records_with_cloned_policies(scan_report.skipped_checks)

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
        records = [record for record in records if record.bc_check_id not in self.policy_level_suppression]  # Filter out policy level suppressions after cloned policy is added
        return records

    def pre_runner(self, runner: _BaseRunner) -> None:
        # not used
        pass

    def post_scan(self, merged_reports: list[Report]) -> None:
        # not used
        pass


integration = CustomPoliciesIntegration(bc_integration)
