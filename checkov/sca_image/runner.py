from __future__ import annotations

import asyncio
import json
import logging
import os.path
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

import requests

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.platform_key import bridgecrew_dir
from checkov.common.bridgecrew.vulnerability_scanning.image_scanner import image_scanner, TWISTCLI_FILE_NAME
from checkov.common.bridgecrew.vulnerability_scanning.integrations.docker_image_scanning import \
    docker_image_scanning_integration
from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.output.report import Report, CheckType, merge_reports
from checkov.common.runners.base_runner import filter_ignored_paths, strtobool
from checkov.common.util.file_utils import compress_file_gzip_base64
from checkov.common.util.dockerfile import is_docker_file
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.runner import Runner as PackageRunner


class Runner(PackageRunner):
    check_type = CheckType.SCA_IMAGE  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__()
        self._check_class: Optional[str] = None
        self._code_repo_path: Optional[Path] = None
        self._check_class = f"{image_scanner.__module__}.{image_scanner.__class__.__qualname__}"
        self.raw_report: Optional[Dict[str, Any]] = None
        self.base_url = bc_integration.api_url
        self.image_referencers: set[ImageReferencer] | None = None

    def should_scan_file(self, filename: str) -> bool:
        return is_docker_file(os.path.basename(filename))

    def scan(
            self,
            image_id: str,
            dockerfile_path: str,
            runner_filter: RunnerFilter | None = None,
    ) -> Dict[str, Any]:
        runner_filter = runner_filter or RunnerFilter()

        # skip complete run, if flag '--check' was used without a CVE check ID
        if runner_filter.checks and all(not check.startswith("CKV_CVE") for check in runner_filter.checks):
            return {}

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return {}

        logging.info(f"SCA image scanning is scanning the image {image_id}")

        cached_results: Dict[str, Any] = image_scanner.get_scan_results_from_cache(image_id)
        if cached_results:
            logging.info(f"Found cached scan results of image {image_id}")
            return cached_results

        image_scanner.setup_scan(image_id, dockerfile_path, skip_extract_image_name=False)
        try:
            output_path = Path(f'results-{image_id}.json')
            scan_result = asyncio.run(self.execute_scan(image_id, output_path))
            self.upload_results_to_cache(output_path, image_id)
            logging.info(f"SCA image scanning successfully scanned the image {image_id}")
            return scan_result
        except Exception:
            raise

    async def execute_scan(
            self,
            image_id: str,
            output_path: Path,
    ) -> Dict[str, Any]:
        command = f"{Path(bridgecrew_dir) / TWISTCLI_FILE_NAME} images scan --address {docker_image_scanning_integration.get_proxy_address()} --token {docker_image_scanning_integration.get_bc_api_key()} --details --output-file \"{output_path}\" {image_id}"
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # log output for debugging
        logging.debug(stdout.decode())

        exit_code = await process.wait()

        if exit_code:
            logging.error(stderr.decode())
            return {}

        # read the report file
        scan_result: Dict[str, Any] = json.loads(output_path.read_text())

        return scan_result

    def upload_results_to_cache(self, output_path: Path, image_id: str) -> None:
        image_id_sha = f"sha256:{image_id}" if not image_id.startswith("sha256:") else image_id

        request_body = {
            "compressedResult": compress_file_gzip_base64(str(output_path)),
            "compressionMethod": "gzip",
            "id": image_id_sha
        }
        response = requests.request(
            "POST", f"{self.base_url}/api/v1/vulnerabilities/scan-results",
            headers=bc_integration.get_default_headers("POST"), data=json.dumps(request_body)
        )

        if response.ok:
            logging.info(f"Successfully uploaded scan results to cache with id={image_id}")
        else:
            logging.info(f"Failed to upload scan results to cache with id={image_id}")

        output_path.unlink()

    def run(
            self,
            root_folder: Union[str, Path],
            external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
            **kwargs: str
    ) -> Report:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        report = Report(self.check_type)

        if "dockerfile_path" in kwargs and "image_id" in kwargs:
            dockerfile_path = kwargs['dockerfile_path']
            image_id = kwargs['image_id']
            return self.get_image_id_report(dockerfile_path, image_id, runner_filter)

        if not files and not root_folder:
            logging.debug("No resources to scan.")
            return report
        if files:
            self.pbar.initiate(len(files))
            for file in files:
                self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(file, root_folder)})
                self.iterate_image_files(file, report, runner_filter)
                self.pbar.update()
            self.pbar.close()

        if root_folder:
            for root, d_names, f_names in os.walk(root_folder):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths)
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths)
                for file in f_names:
                    abs_fname = os.path.join(root, file)
                    self.iterate_image_files(abs_fname, report, runner_filter)
        return report

    def iterate_image_files(self, abs_fname: str, report: Report, runner_filter: RunnerFilter) -> None:
        """
        Get workflow file, and get the list of images from every relevant imagereferencer, and create a unified vulnrability report
        :param abs_fname: file path to inspect
        :param report: unified report object
        :param runner_filter: filter for report
        """
        if not self.image_referencers:
            return
        for image_referencer in self.image_referencers:
            if image_referencer.is_workflow_file(abs_fname):
                images = image_referencer.get_images(file_path=abs_fname)
                for image in images:
                    image_report = self.get_image_report(dockerfile_path=abs_fname, image=image,
                                                         runner_filter=runner_filter)
                    merge_reports(report, image_report)

    def get_image_report(self, dockerfile_path: str, image: Image, runner_filter: RunnerFilter) -> Report:
        """

        :param dockerfile_path: path of a file that might contain a container image
        :param image: Image object
        :param runner_filter:
        :return: vulnerability report
        """
        report = Report(self.check_type)

        # skip complete run, if flag '--check' was used without a CVE check ID
        if runner_filter.checks and all(not check.startswith("CKV_CVE") for check in runner_filter.checks):
            return report

        cached_results: Dict[str, Any] = image_scanner.get_scan_results_from_cache(f"image:{image.name}")
        if cached_results:
            logging.info(f"Found cached scan results of image {image.name}")

            self.raw_report = cached_results
            result = cached_results.get('results', [{}])[0]
            vulnerabilities = result.get("vulnerabilities") or []
            image_id = self.extract_image_short_id(result)

            self.parse_vulns_to_records(
                report=report,
                result=result,
                rootless_file_path=f"{dockerfile_path} ({image.name} lines:{image.start_line}-{image.end_line} ({image_id}))",
                runner_filter=runner_filter,
                vulnerabilities=vulnerabilities,
                packages=[],
                file_abs_path=os.path.abspath(dockerfile_path),
            )

            return report
        elif strtobool(os.getenv("CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING", "False")):
            # experimental flag on running image referencers via local twistcli
            image_id = ImageReferencer.inspect(image.name)
            scan_result = self.scan(image_id, dockerfile_path, runner_filter)
            if scan_result is None:
                return report

            self.raw_report = scan_result
            result = scan_result.get('results', [{}])[0]
            vulnerabilities = result.get("vulnerabilities") or []
            self.parse_vulns_to_records(
                report=report,
                result=result,
                rootless_file_path=f"{dockerfile_path} ({image.name} lines:{image.start_line}-{image.end_line} ({image_id}))",
                runner_filter=runner_filter,
                vulnerabilities=vulnerabilities,
                packages=[],
                file_abs_path=os.path.abspath(dockerfile_path),
            )
        else:
            logging.info(f"No cache hit for image {image.name}")

        return report

    def get_image_id_report(self, dockerfile_path: str, image_id: str, runner_filter: RunnerFilter) -> Report:
        """
        THIS METHOD HANDLES CUSTOM IMAGE SCANNING THAT COMES DIRECTLY FROM CLI PARAMETERS
        """
        report = Report(self.check_type)

        scan_result = self.scan(image_id, dockerfile_path, runner_filter)
        if scan_result is None:
            return report
        self.raw_report = scan_result
        result = scan_result.get('results', [{}])[0]
        vulnerabilities = result.get("vulnerabilities") or []
        self.parse_vulns_to_records(
            report=report,
            result=result,
            rootless_file_path=f"{dockerfile_path} ({image_id})",
            runner_filter=runner_filter,
            vulnerabilities=vulnerabilities,
            packages=[],
            file_abs_path=os.path.abspath(dockerfile_path)
        )
        return report

    def extract_image_short_id(self, scan_result: dict[str, Any]) -> str:
        """Extracts a shortened version of the image ID from the scan result"""

        if "id" not in scan_result:
            return "sha256:unknown"

        image_id: str = scan_result["id"]

        if image_id.startswith("sha256:"):
            return image_id[:17]
        return image_id[:10]
