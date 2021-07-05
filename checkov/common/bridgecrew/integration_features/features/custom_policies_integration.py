import json
import logging

import requests

from checkov.common.bridgecrew.integration_features.base_integration_feature import BaseIntegrationFeature
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import get_default_get_headers, get_auth_header, extract_error_message
from checkov.terraform.checks_infra.checks_parser import NXGraphCheckParser
from checkov.terraform.runner import graph_registry


class CustomPoliciesIntegration(BaseIntegrationFeature):

    def __init__(self, bc_integration):
        super().__init__(bc_integration, order=0)
        self.policies = {}
        self.platform_policy_parser = NXGraphCheckParser()

    def is_valid(self):
        return self.bc_integration.is_integration_configured() and not self.bc_integration.skip_policy_download

    def pre_scan(self):
        self.policies = self._get_policies_from_platform()
        for policy in self.policies:
            check = self.platform_policy_parser.parse_raw_check(self._convert_raw_check(policy))
            graph_registry.checks.append(check)
        logging.debug(f'Found {len(self.policies)} custom policies from the platform.')

    @staticmethod
    def _convert_raw_check(policy):
        metadata = {
            'id': policy['id'],
            'name': policy['title'],
            'category': policy['category']
        }
        check = {
            'metadata': metadata,
            'definition': policy['conditionQuery']
        }
        return check

    def _get_policies_from_platform(self):
        headers = merge_dicts(get_default_get_headers(self.bc_integration.bc_source, self.bc_integration.bc_source_version),
                              get_auth_header(self.bc_integration.bc_api_key))
        response = requests.request('GET', self.policies_url, headers=headers)

        if response.status_code != 200:
            error_message = extract_error_message(response)
            raise Exception(f'Get custom policies request failed with response code {response.status_code}: {error_message}')

        policies = response.json().get('data', [])
        return policies


integration = CustomPoliciesIntegration(bc_integration)
