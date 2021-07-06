import logging
import os
import platform
import stat
import requests
from datetime import datetime, timedelta

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.integration_features.base_integration_feature import BC_API_URL
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.http_utils import get_auth_header, get_default_get_headers, get_default_post_headers


class DockerImageScanningIntegration:
    docker_image_scanning_base_url = f"{BC_API_URL}/vulnerabilities/docker-images"

    def get_bc_api_key(self):
        return bc_integration.bc_api_key

    def get_proxy_address(self):
        return f"{self.docker_image_scanning_base_url}/twistcli/proxy"

    def download_twistcli(self, cli_file_name):
        os_type = platform.system().lower()
        headers = merge_dicts(
            get_default_get_headers(bc_integration.bc_source, bc_integration.bc_source_version),
            get_auth_header(bc_integration.bc_api_key)
        )
        response = requests.request('GET', f"{self.docker_image_scanning_base_url}/twistcli/download?os={os_type}", headers=headers)
        open(cli_file_name, 'wb').write(response.content)
        st = os.stat(cli_file_name)
        os.chmod(cli_file_name, st.st_mode | stat.S_IEXEC)
        logging.debug(f'TwistCLI downloaded and has execute permission')

    def report_results(self, docker_image_name, dockerfile_path, dockerfile_content, twistcli_scan_result):
        headers = merge_dicts(
            get_default_post_headers(bc_integration.bc_source, bc_integration.bc_source_version),
            get_auth_header(bc_integration.bc_api_key)
        )
        vulnerabilities = list(map(lambda x: {
            'cveId': x['id'],
            'status': x.get('status', 'open'),
            'severity': x['severity'],
            'packageName': x['packageName'],
            'packageVersion': x['packageVersion'],
            'link': x['link'],
            'cvss': x.get('cvss'),
            'vector': x.get('vector'),
            'description': x.get('description'),
            'riskFactors': x.get('riskFactors'),
            'publishedDate': x.get('publishedDate') or (datetime.now() - timedelta(days=x.get('publishedDays', 0))).isoformat()
        }, twistcli_scan_result['results'][0].get('vulnerabilities', [])))
        payload = {
            'sourceId': bc_integration.repo_id,
            'branch': bc_integration.repo_branch,
            'dockerImageName': docker_image_name,
            'dockerFilePath': dockerfile_path,
            'dockerFileContent': dockerfile_content,
            'sourceType': bc_integration.bc_source,
            'vulnerabilities': vulnerabilities
        }
        response = requests.request('POST', f"{self.docker_image_scanning_base_url}/report", headers=headers, json=payload)
        response.raise_for_status()

docker_image_scanning_integration = DockerImageScanningIntegration()
