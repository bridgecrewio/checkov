import logging
import platform
import subprocess  # nosec
import os
import stat
import urllib.request

from checkov.common.bridgecrew.image_scanning.twistlock_integration import twistlock_integration

TWISTLOCK_CLI_FILE_NAME = 'twistcli'


class ImageScanner:
    def scan(self, docker_image_id):
        os_type = platform.system().lower()
        twistlock_download_link = twistlock_integration.get_download_link(os_type)
        logging.debug(f'TwistLock CLI download link: {twistlock_download_link}')

        urllib.request.urlretrieve(twistlock_download_link,
                                   TWISTLOCK_CLI_FILE_NAME)  # nosec - validated the URL in the integration
        st = os.stat(TWISTLOCK_CLI_FILE_NAME)
        os.chmod(TWISTLOCK_CLI_FILE_NAME, st.st_mode | stat.S_IEXEC)
        logging.debug('TwistLock CLI downloaded and set execute permission successfully')

        command_args = f"./twistcli images scan --address {twistlock_integration.get_proxy_address()} --token {twistlock_integration.get_bc_api_key()} --details --output-file results.json {docker_image_id}".split()
        subprocess.run(command_args, stdout=subprocess.DEVNULL)  # nosec
        logging.debug(f'TwistLock CLI ran successfully on image {docker_image_id}')


image_scanner = ImageScanner()
