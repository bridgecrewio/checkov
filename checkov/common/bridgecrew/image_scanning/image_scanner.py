import subprocess

BRIDGECREW_TWISTLOCK_PROXY_ADDRESS = "https://us-east1.cloud.twistlock.com/us-2-158290583"

class ImageScanner:
    def scan(self, bc_api_key, docker_image_id):
        command_args = f"./twistcli images scan --address {BRIDGECREW_TWISTLOCK_PROXY_ADDRESS} --token {bc_api_key} --details --output-file results.json {docker_image_id}".split()
        subprocess.run(command_args, stdout=subprocess.DEVNULL)

image_scanner = ImageScanner()