from __future__ import annotations

import asyncio
import json
import logging
import os.path
from collections.abc import Iterable
from pathlib import Path
from typing import Optional, Union, Dict, Any

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.platform_key import bridgecrew_dir
from checkov.common.bridgecrew.vulnerability_scanning.image_scanner import image_scanner, TWISTCLI_FILE_NAME
from checkov.common.bridgecrew.vulnerability_scanning.integrations.docker_image_scanning import \
    docker_image_scanning_integration
from checkov.common.images.image_referencer import ImageReferencer, Image
from checkov.common.output.report import Report, merge_reports
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.common import ImageDetails
from checkov.common.models.enums import ErrorStatus
from checkov.common.runners.base_runner import filter_ignored_paths, strtobool
from checkov.common.sca.commons import should_run_scan
from checkov.common.sca.output import add_to_report_sca_data, get_license_statuses
from checkov.common.util.file_utils import compress_file_gzip_base64
from checkov.common.util.dockerfile import is_dockerfile
from checkov.common.util.http_utils import request_wrapper
from checkov.runner_filter import RunnerFilter
from checkov.sca_package_2.runner import Runner as PackageRunner


class Runner(PackageRunner):
    check_type = CheckType.SCA_IMAGE  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__(report_type=self.check_type)
        self._check_class: Optional[str] = None
        self._code_repo_path: Optional[Path] = None
        self._check_class = f"{image_scanner.__module__}.{image_scanner.__class__.__qualname__}"
        self.raw_report: Optional[Dict[str, Any]] = None
        self.base_url = bc_integration.api_url
        self.image_referencers: set[ImageReferencer] | None = None

    def should_scan_file(self, filename: str) -> bool:
        return is_dockerfile(os.path.basename(filename))

    def scan(
            self,
            image_id: str,
            dockerfile_path: str,
            runner_filter: RunnerFilter | None = None,
    ) -> Dict[str, Any] | None:
        runner_filter = runner_filter or RunnerFilter()

        # skip complete run, if flag '--check' was used without a CVE check ID or the license policies
        if not should_run_scan(runner_filter.checks):
            return {}

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return {}

        logging.info(f"SCA image scanning is scanning the image {image_id}")

        cached_results: Dict[str, Any] | None = image_scanner.get_scan_results_from_cache(image_id)
        if cached_results:
            logging.info(f"Found cached scan results of image {image_id}")
            return cached_results

        setup_status: bool = image_scanner.setup_scan(image_id, dockerfile_path, skip_extract_image_name=False)
        if not setup_status:
            return None
        if not setup_status:
            return None
        output_path = Path(f'results-{image_id}.json')
        scan_result = asyncio.run(self.execute_scan(image_id, output_path))
        self.upload_results_to_cache(output_path, image_id)
        logging.info(f"SCA image scanning successfully scanned the image {image_id}")
        return scan_result

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
        try:
            logging.debug(stdout.decode())
        except UnicodeDecodeError:
            logging.error("error was caught when trying to decode the \'stdout\' from twistcli.\n"
                          f"file content is:\n{image_scanner.dockerfile_content}.\n"
                          f"twistcli command is \'{command}\'", exc_info=True)

        exit_code = await process.wait()

        if exit_code:
            logging.error(f"error when running twistcli on image_id {image_id}")
            logging.error(stderr.decode())
            return {}

        # read the report file
        scan_result: Dict[str, Any] = json.loads(output_path.read_text())

        return scan_result

    def upload_results_to_cache(self, output_path: Path, image_id: str) -> None:
        try:
            image_id_sha = f"sha256:{image_id}" if not image_id.startswith("sha256:") else image_id

            request_body = {
                "compressedResult": compress_file_gzip_base64(str(output_path)),
                "compressionMethod": "gzip",
                "id": image_id_sha
            }
            response = request_wrapper(
                "POST", f"{self.base_url}/api/v1/vulnerabilities/scan-results",
                headers=bc_integration.get_default_headers("POST"), data=json.dumps(request_body)
            )

            if response.ok:
                logging.info(f"Successfully uploaded scan results to cache with id={image_id}")
            else:
                logging.info(f"Failed to upload scan results to cache with id={image_id}")

            output_path.unlink()
        except Exception:
            logging.debug(
                "Unexpected failure happened during uploading results to cache. details are below.\n"
                "Note that the scan is still running. if this is repeated, please report.", exc_info=True)

    def run(
            self,
            root_folder: str | Path | None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
            **kwargs: str
    ) -> Report | list[Report]:
        runner_filter = runner_filter or RunnerFilter()
        if not runner_filter.show_progress_bar:
            self.pbar.turn_off_progress_bar()

        self._code_repo_path = Path(root_folder) if root_folder else None

        if "dockerfile_path" in kwargs and "image_id" in kwargs:
            dockerfile_path = kwargs['dockerfile_path']
            image_id = kwargs['image_id']
            return self.get_image_id_report(dockerfile_path, image_id, runner_filter)
        report = Report(self.check_type)
        if not files and not root_folder:
            logging.debug("No resources to scan.")
            return report
        if files:
            self.pbar.initiate(len(files))
            # 'root_folder' should contain the common prefix so the absolute full path can be shortened later
            root_folder = os.path.split(os.path.commonprefix(files))[0]

            for file in files:
                self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(file, root_folder)})
                self.iterate_image_files(file, report, runner_filter)
                self.pbar.update()
            self.pbar.close()
        if self._code_repo_path:
            for root, d_names, f_names in os.walk(self._code_repo_path):
                filter_ignored_paths(root, d_names, runner_filter.excluded_paths, included_paths=self.included_paths())
                filter_ignored_paths(root, f_names, runner_filter.excluded_paths, included_paths=self.included_paths())
                for file in f_names:
                    abs_fname = os.path.join(root, file)
                    self.iterate_image_files(abs_fname, report, runner_filter, self._code_repo_path)
        return report

    def iterate_image_files(self, abs_fname: str, report: Report, runner_filter: RunnerFilter,
                            root_folder: Union[str, Path, None] = None) -> None:
        """
        Get workflow file, and get the list of images from every relevant imagereferencer, and create a unified vulnrability report
        :param root_folder: for CLI scans - the directory in which checkov runs
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
                    image_cached_result: Dict[str, Any] | None = image_scanner.get_scan_results_from_cache(
                        f"image:{image.name}")

                    image_cached_report: dict[str, Any] = self.get_image_cached_results(dockerfile_path=abs_fname,
                                                                                        image=image,
                                                                                        image_cached_result=image_cached_result,
                                                                                        root_folder=root_folder)
                    if image_cached_report:
                        report.image_cached_results.append(image_cached_report)

                    if strtobool(os.getenv('CHECKOV_CREATE_SCA_IMAGE_REPORTS_FOR_IR', "True")):
                        image_report = self.get_image_report(dockerfile_path=abs_fname, image=image,
                                                             runner_filter=runner_filter,
                                                             image_cached_result=image_cached_result)
                        merge_reports(report, image_report)

    def get_report_from_scan_result(self, result: Dict[str, Any], dockerfile_path: str, rootless_file_path: str,
                                    image_details: ImageDetails | None, runner_filter: RunnerFilter) -> Report:
        report = Report(self.check_type)
        vulnerabilities = result.get("vulnerabilities", [])
        packages = result.get("packages", [])
        license_statuses = get_license_statuses(packages)

        add_to_report_sca_data(
            report=report,
            check_class=self._check_class,
            scanned_file_path=os.path.abspath(dockerfile_path),
            rootless_file_path=rootless_file_path,
            runner_filter=runner_filter,
            vulnerabilities=vulnerabilities,
            packages=packages,
            license_statuses=license_statuses,
            sca_details=image_details,
            report_type=self.report_type
        )
        return report

    def get_image_cached_results(self, dockerfile_path: str, image: Image, image_cached_result: Dict[str, Any] | None,
                                 root_folder: Union[str, Path, None] = None) -> dict[str, Any]:
        """
            :param image_cached_result: twistcli result for image as saved in cache
            :param root_folder: for CLI scans - the directory in which checkov runs
            :param dockerfile_path: path of a file that might contain a container image
            :param image: Image object
            :return: cached_results report
        """

        if not image_cached_result:
            # TODO: do we want to trigger a scan in this case?
            logging.info(
                f"No cache hit for image {image.name} when getting cached results for dockerfile {dockerfile_path}")
            return {}
        payload: dict[str, Any] = docker_image_scanning_integration.create_report(
            twistcli_scan_result=image_cached_result,
            bc_platform_integration=bc_integration,
            file_path=dockerfile_path,
            file_content=f'image: {image.name}',
            docker_image_name=image.name,
            related_resource_id=image.related_resource_id,
            root_folder=root_folder,
            error_lines=[image.start_line, image.end_line])
        return payload

    def get_image_report(self, dockerfile_path: str, image: Image, runner_filter: RunnerFilter,
                         image_cached_result: Dict[str, Any] | None) -> Report:
        """

        :param dockerfile_path: path of a file that might contain a container image
        :param image: Image object
        :param runner_filter:
        :return: vulnerability report
        """
        # skip complete run, if flag '--check' was used without a CVE check ID
        if not should_run_scan(runner_filter.checks):
            return Report(self.check_type)

        if image_cached_result:
            logging.info(f"Found cached scan results of image {image.name}")
            self.raw_report = image_cached_result
            result = image_cached_result.get('results', [{}])[0]
            image_id = self.extract_image_short_id(result)
            image_details = self.get_image_details_from_twistcli_result(scan_result=result, image_id=image_id,
                                                                        image_name=image.name,
                                                                        related_resource_id=image.related_resource_id)
            if self._code_repo_path:
                try:
                    dockerfile_path = str(Path(dockerfile_path).relative_to(self._code_repo_path))
                except ValueError:
                    # Path.is_relative_to() was implemented in Python 3.9
                    pass
            rootless_file_path = dockerfile_path.replace(Path(dockerfile_path).anchor, "", 1)
            rootless_file_path_to_report = f"{rootless_file_path} ({image.name} lines:{image.start_line}-" \
                                           f"{image.end_line} ({image_id}))"
            return self.get_report_from_scan_result(result, dockerfile_path, rootless_file_path_to_report,
                                                    image_details, runner_filter)
        else:
            logging.info(f"No cache hit for image {image.name}")

        return Report(self.check_type)

    def get_image_id_report(self, dockerfile_path: str, image_id: str, runner_filter: RunnerFilter) -> Report:
        """
        THIS METHOD HANDLES CUSTOM IMAGE SCANNING THAT COMES DIRECTLY FROM CLI PARAMETERS
        """
        scan_result = self.scan(image_id, dockerfile_path, runner_filter)
        if scan_result is None:
            report = Report(self.check_type)
            report.set_error_status(ErrorStatus.ERROR)
            return report
        self.raw_report = scan_result
        result = scan_result.get('results', [{}])[0]
        image_details = self.get_image_details_from_twistcli_result(scan_result=result, image_id=image_id)
        if self._code_repo_path:
            try:
                dockerfile_path = str(Path(dockerfile_path).relative_to(self._code_repo_path))
            except ValueError:
                # Path.is_relative_to() was implemented in Python 3.9
                pass
        rootless_file_path = dockerfile_path.replace(Path(dockerfile_path).anchor, "", 1)
        rootless_file_path_to_report = f"{rootless_file_path} ({image_id})"
        return self.get_report_from_scan_result(result, dockerfile_path, rootless_file_path_to_report, image_details,
                                                runner_filter)

    def extract_image_short_id(self, scan_result: dict[str, Any]) -> str:
        """Extracts a shortened version of the image ID from the scan result"""

        if "id" not in scan_result:
            return "sha256:unknown"

        image_id: str = scan_result["id"]

        if image_id.startswith("sha256:"):
            return image_id[:17]
        return image_id[:10]

    def get_image_details_from_twistcli_result(self, scan_result: dict[str, Any], image_id: str,
                                               image_name: str | None = None,
                                               related_resource_id: str | None = None) -> ImageDetails:
        image_packages = scan_result.get('packages', [])
        image_package_types = {
            f'{package["name"]}@{package["version"]}': package['type']
            for package in image_packages
        }
        return ImageDetails(
            distro=scan_result.get('distro', ''),
            distro_release=scan_result.get('distroRelease', ''),
            package_types=image_package_types,
            image_id=image_id,
            name=image_name,
            related_resource_id=related_resource_id
        )

    def included_paths(self) -> Iterable[str]:
        return ['.github', '.circleci']
