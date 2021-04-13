import logging
import os
import platform
import stat
import requests

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.integration_features.base_integration_feature import BC_API_URL
from checkov.common.util.dict_utils import merge_dicts
from checkov.common.util.http_utils import get_auth_header, get_default_get_headers


class DockerImageScanningIntegration:
    docker_image_scanning_base_url = f"{BC_API_URL}/vulnerabilities/docker-images"

    def get_bc_api_key(self):
        return bc_integration.bc_api_key

    def get_proxy_address(self):
        return f"{self.docker_image_scanning_base_url}/twistcli-proxy"

    def download_twistcli(self, cli_file_name):
        os_type = platform.system().lower()
        headers = merge_dicts(
            get_default_get_headers(bc_integration.bc_source, bc_integration.bc_source_version),
            get_auth_header(bc_integration.bc_api_key)
        )
        response = requests.request('GET', f"{self.docker_image_scanning_base_url}/download-twistcli?os={os_type}", headers=headers)
        open(cli_file_name, 'wb').write(response.content)
        st = os.stat(cli_file_name)
        os.chmod(cli_file_name, st.st_mode | stat.S_IEXEC)
        logging.debug(f'TwistCLI downloaded and has execute permission')


docker_image_scanning_integration = DockerImageScanningIntegration()
