import logging
import subprocess  # nosec

from checkov.common.bridgecrew.image_scanning.docker_image_scanning_integration import docker_image_scanning_integration

TWISTCLI_FILE_NAME = 'twistcli'


class ImageScanner:
    def scan(self, docker_image_id):
        docker_image_scanning_integration.download_twistcli(TWISTCLI_FILE_NAME)

        command_args = f"./{TWISTCLI_FILE_NAME} images scan --address {docker_image_scanning_integration.get_proxy_address()} --token {docker_image_scanning_integration.get_bc_api_key()} --details --output-file results.json {docker_image_id}".split()
        subprocess.run(command_args, stdout=subprocess.DEVNULL)  # nosec
        logging.debug(f'TwistCLI ran successfully on image {docker_image_id}')


image_scanner = ImageScanner()
