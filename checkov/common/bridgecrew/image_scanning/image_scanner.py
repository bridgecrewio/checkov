import logging
import subprocess  # nosec
import docker
import json
import os

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
    def scan(self, docker_image_id, dockerfile_path):
        try:
            docker_image_name = _get_docker_image_name(docker_image_id)
            dockerfile_content = _get_dockerfile_content(dockerfile_path)
            docker_image_scanning_integration.download_twistcli(TWISTCLI_FILE_NAME)

            command_args = f"./{TWISTCLI_FILE_NAME} images scan --address {docker_image_scanning_integration.get_proxy_address()} --token {docker_image_scanning_integration.get_bc_api_key()} --details --output-file {DOCKER_IMAGE_SCAN_RESULT_FILE_NAME} {docker_image_id}".split()
            subprocess.run(command_args)  # nosec
            logging.info(f'TwistCLI ran successfully on image {docker_image_id}')

            with open(DOCKER_IMAGE_SCAN_RESULT_FILE_NAME) as docker_image_scan_result_file:
                scan_result = json.load(docker_image_scan_result_file)

            docker_image_scanning_integration.report_results(docker_image_name, dockerfile_path, dockerfile_content, twistcli_scan_result=scan_result)
            logging.info(f'Docker image scanning results reported to the platform')

            os.remove(TWISTCLI_FILE_NAME)
            logging.info(f'twistcli file removed')
        except Exception as e:
            logging.error(f"Failed to scan docker image\n{e}")
            raise e



image_scanner = ImageScanner()
