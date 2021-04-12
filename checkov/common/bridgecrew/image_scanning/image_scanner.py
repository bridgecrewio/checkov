import logging
import subprocess  # nosec

from checkov.common.bridgecrew.image_scanning.twistlock_integration import twistlock_integration

TWISTLOCK_CLI_FILE_NAME = 'twistcli'


class ImageScanner:
    def scan(self, docker_image_id):
        twistlock_integration.download_cli(TWISTLOCK_CLI_FILE_NAME)

        command_args = f"./twistcli images scan --address {twistlock_integration.get_proxy_address()} --token {twistlock_integration.get_bc_api_key()} --details --output-file results.json {docker_image_id}".split()
        subprocess.run(command_args, stdout=subprocess.DEVNULL)  # nosec
        logging.debug(f'TwistLock CLI ran successfully on image {docker_image_id}')


image_scanner = ImageScanner()
