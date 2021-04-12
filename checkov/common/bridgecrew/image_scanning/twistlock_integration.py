import json
import logging

import requests

from checkov.common.bridgecrew.integration_features.base_integration_feature import BC_API_URL
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.dict_utils import merge_dicts
from checkov.common.util.http_utils import get_auth_header, extract_error_message, get_default_get_headers


class TwistLockIntegration:
    # twistlock_base_url = f"{BC_API_URL}/vulnerabilities/twistlock"
    twistlock_base_url = "http://localhost:3009/api/v1/vulnerabilities/twistlock"

    def get_bc_api_key(self):
        return bc_integration.bc_api_key

    def get_proxy_address(self):
        return f"{self.twistlock_base_url}/proxy"

    def get_download_link(self, os_type):
        headers = merge_dicts(
            get_default_get_headers(bc_integration.bc_source, bc_integration.bc_source_version),
            get_auth_header(bc_integration.bc_api_key)
        )
        response = requests.request('GET', f"{self.twistlock_base_url}/download-link?os={os_type}", headers=headers)

        if response.status_code != 200:
            error_message = extract_error_message(response)
            raise Exception(f'Get TwistLock download link request failed with response code {response.status_code}: {error_message}')

        logging.debug(f'Response from TwistLock download link endpoint: {response.content}')

        download_link_result = json.loads(response.content) if response.content else None
        download_link = download_link_result['data']

        if not download_link.startswith('https://'):
            raise Exception(f'Invalid URL received from TwistLock download endpoint {download_link}')

        return download_link

twistlock_integration = TwistLockIntegration()