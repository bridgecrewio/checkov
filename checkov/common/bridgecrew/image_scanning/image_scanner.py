import logging
import subprocess  # nosec
import docker
import json
import os
import time

from checkov.common.bridgecrew.image_scanning.docker_image_scanning_integration import docker_image_scanning_integration

TWISTCLI_FILE_NAME = 'twistcli'
DOCKER_IMAGE_SCAN_RESULT_FILE_NAME = 'docker-image-scan-results.json'


def _get_docker_image_name(docker_image_id):
    try:
        docker_client = docker.from_env()
        return docker_client.images.get(docker_image_id).attrs['RepoDigests'][0].split('@')[0]
    except Exception as e:
        logging.error(f"docker image needs to have repository")
        raise e


def _get_dockerfile_content(dockerfile_path):
    try:
        with open(dockerfile_path) as f:
            return f.read()
    except FileNotFoundError as e:
        logging.error(f"Path to Dockerfile is invalid\n{e}")
        raise e
    except Exception as e:
        logging.error(f"Failed to read Dockerfile content\n{e}")
        raise e


class ImageScanner:
    def __init__(self):
        self.docker_image_name = ''
        self.dockerfile_content = ''

    def setup_scan(self, docker_image_id, dockerfile_path, skip_extract_image_name):
        try:
            if skip_extract_image_name:
                # Provide a default image name in case the image has not been tagged with a name
                self.docker_image_name = f'repository/image{str(time.time() * 1000)}'
            else:
                self.docker_image_name = _get_docker_image_name(docker_image_id)
            self.dockerfile_content = _get_dockerfile_content(dockerfile_path)
            docker_image_scanning_integration.download_twistcli(TWISTCLI_FILE_NAME)
        except Exception as e:
            logging.error(f"Failed to setup docker image scanning\n{e}")
            raise e

    @staticmethod
    def cleanup_scan():
        os.remove(TWISTCLI_FILE_NAME)
        logging.info(f'twistcli file removed')

    @staticmethod
    def run_image_scan(docker_image_id):
        command_args = f"./{TWISTCLI_FILE_NAME} images scan --address {docker_image_scanning_integration.get_proxy_address()} --token {docker_image_scanning_integration.get_bc_api_key()} --details --output-file {DOCKER_IMAGE_SCAN_RESULT_FILE_NAME} {docker_image_id}".split()
        subprocess.run(command_args, check=True, shell=True)  # nosec
        logging.info(f'TwistCLI ran successfully on image {docker_image_id}')

        with open(DOCKER_IMAGE_SCAN_RESULT_FILE_NAME) as docker_image_scan_result_file:
            scan_result = json.load(docker_image_scan_result_file)
        return scan_result

    def scan(self, docker_image_id, dockerfile_path, skip_extract_image_name=False):
        try:
            self.setup_scan(docker_image_id, dockerfile_path, skip_extract_image_name)
            scan_result = self.run_image_scan(docker_image_id)
            docker_image_scanning_integration.report_results(self.docker_image_name, dockerfile_path,
                                                             self.dockerfile_content,
                                                             twistcli_scan_result=scan_result)
            logging.info(f'Docker image scanning results reported to the platform')
            self.cleanup_scan()
        except Exception as e:
            logging.error(f"Failed to scan docker image\n{e}")
            raise e


image_scanner = ImageScanner()
