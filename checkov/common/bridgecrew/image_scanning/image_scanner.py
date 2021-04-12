import subprocess
import os

from checkov.common.bridgecrew.integration_features.features.twistlock_integration import integration as twistlock_integration

BRIDGECREW_TWISTLOCK_PROXY_ADDRESS = "https://us-east1.cloud.twistlock.com/us-2-158290583"

class ImageScanner:
    def scan(self, bc_api_key, docker_image_id):
        command_args = f"./twistcli images scan --address {twistlock_integration.get_proxy_address()} --token {bc_api_key} --details --output-file results.json {docker_image_id}".split()
        subprocess.run(command_args, stdout=subprocess.DEVNULL)

image_scanner = ImageScanner()