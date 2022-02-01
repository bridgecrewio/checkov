import logging
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List

import requests
import re

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry, get_graph_checks_registry
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import get_default_get_headers, get_auth_header, extract_error_message

# service-provider::service-name::data-type-name
CFN_RESOURCE_TYPE_IDENTIFIER = re.compile(r"^[a-zA-Z0-9]+::[a-zA-Z0-9]+::[a-zA-Z0-9]+$")


class CustomPoliciesIntegration(BaseIntegrationFeature):
    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.policies = {}
        self.platform_policy_parser = NXGraphCheckParser()
        self.policies_url = f"{self.bc_integration.api_url}/api/v1/policies/table/data"
        self.bc_cloned_checks: Dict[str, List[dict]] = defaultdict(list)

    def is_valid(self) -> bool:
        return (
            self.bc_integration.is_integration_configured()
            and not self.bc_integration.skip_policy_download
            and not self.integration_feature_failures
        )

    def pre_scan(self):
        try:
            self.policies = self._get_policies_from_platform()
            for policy in self.policies:
                converted_check = self._convert_raw_check(policy)
                source_incident_id = policy.get('sourceIncidentId')
                if source_incident_id:
                    self.bc_cloned_checks[source_incident_id].append(policy)
                    continue
                resource_types = Registry._get_resource_types(converted_check['metadata'])
                check = self.platform_policy_parser.parse_raw_check(converted_check, resources_types=resource_types)
                if re.match(CFN_RESOURCE_TYPE_IDENTIFIER, check.resource_types[0]):
                    get_graph_checks_registry("cloudformation").checks.append(check)
                else:
                    get_graph_checks_registry("terraform").checks.append(check)
            logging.debug(f'Found {len(self.policies)} custom policies from the platform.')
        except Exception as e:
            self.integration_feature_failures = True
            logging.debug(f'{e} \nScanning without applying custom policies from the platform.', exc_info=True)

    @staticmethod
    def _convert_raw_check(policy):
        metadata = {
            'id': policy['id'],
            'name': policy['title'],
            'category': policy['category'],
            'scope': {
                'provider': policy['provider']
            }
        }
        check = {
            'metadata': metadata,
            'definition': policy['conditionQuery']
        }
        return check

    def _get_policies_from_platform(self):
        headers = merge_dicts(get_default_get_headers(self.bc_integration.bc_source, self.bc_integration.bc_source_version),
                              get_auth_header(self.bc_integration.get_auth_token()))
        response = requests.request('GET', self.policies_url, headers=headers)

        if response.status_code != 200:
            error_message = extract_error_message(response)
            raise Exception(f'Get custom policies request failed with response code {response.status_code}: {error_message}')

        policies = response.json().get('data', [])
        policies = [p for p in policies if p['isCustom']]
        return policies

    def post_runner(self, scan_reports):
        if self.bc_cloned_checks:
            scan_reports.failed_checks = self.extend_records_with_cloned_policies(scan_reports.failed_checks)
            scan_reports.passed_checks = self.extend_records_with_cloned_policies(scan_reports.passed_checks)
            scan_reports.skipped_checks = self.extend_records_with_cloned_policies(scan_reports.skipped_checks)

    def extend_records_with_cloned_policies(self, records):
        bc_check_ids = [record.bc_check_id for record in records]
        for idx, bc_check_id in enumerate(bc_check_ids):
            cloned_policies = self.bc_cloned_checks.get(bc_check_id, [])
            for cloned_policy in cloned_policies:
                new_record = deepcopy(records[idx])
                new_record.check_id = cloned_policy['id']
                new_record.bc_check_id = cloned_policy['id']
                new_record.guideline = cloned_policy['guideline']
                new_record.severity = cloned_policy['severity']
                new_record.check_name = cloned_policy['title']
                records.append(new_record)
        return records


integration = CustomPoliciesIntegration(bc_integration)
