import asyncio
import json
import logging
import os.path
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.vulnerability_scanning.image_scanner import image_scanner, TWISTCLI_FILE_NAME
from checkov.common.bridgecrew.vulnerability_scanning.integrations.docker_image_scanning import \
    docker_image_scanning_integration
from checkov.common.images.image_referencer import ImageReferencer
from checkov.common.output.report import Report, CheckType, merge_reports
from checkov.common.runners.base_runner import filter_ignored_paths, strtobool
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.runner import Runner as PackageRunner


class Runner(PackageRunner):
    check_type = CheckType.SCA_IMAGE

    def __init__(self) -> None:
        self._check_class: Optional[str] = None
        self._code_repo_path: Optional[Path] = None
        self._check_class = f"{image_scanner.__module__}.{image_scanner.__class__.__qualname__}"
        self.raw_report: Optional[Dict[str, Any]] = None
        self.image_referencers: Optional[ImageReferencer] = None

    def scan(
            self,
            image_id: str,
            dockerfile_path: str,
            runner_filter: RunnerFilter = RunnerFilter(),
    ) -> Dict[Any,Any]:

        # skip complete run, if flag '--check' was used without a CVE check ID
        if runner_filter.checks and all(not check.startswith("CKV_CVE") for check in runner_filter.checks):
            return {}

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return {}

        logging.info(f"SCA image scanning is scanning the image {image_id}")
        image_scanner.setup_scan(image_id, dockerfile_path, skip_extract_image_name=False)
        try:
            scan_result = asyncio.run(self.execute_scan(image_id, Path('results.json')))
            logging.info(f"SCA image scanning successfully scanned the image {image_id}")
            image_scanner.cleanup_scan()
            return scan_result
        except Exception:
            image_scanner.cleanup_scan()
            raise

    @staticmethod
    async def execute_scan(
            image_id: str,
            output_path: Path,
    ) -> Dict[str, Any]:
        command = f"./{TWISTCLI_FILE_NAME} images scan --address {docker_image_scanning_integration.get_proxy_address()} --token {docker_image_scanning_integration.get_bc_api_key()} --details --output-file \"{output_path}\" {image_id}"
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

        # read and delete the report file
        scan_result: Dict[str, Any] = json.loads(output_path.read_text())
        output_path.unlink()

        return scan_result

    def run(
            self,
            root_folder: Union[str, Path],
            external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            runner_filter: RunnerFilter = RunnerFilter(),
            collect_skip_comments: bool = True,
            **kwargs: str
    ) -> Report:
        report = Report(self.check_type)

        if "dockerfile_path" in kwargs and "image_id" in kwargs:
            dockerfile_path = kwargs['dockerfile_path']
            image_id = kwargs['image_id']
            return self.get_image_report(dockerfile_path, image_id, runner_filter)

        if not strtobool(os.getenv("CHECKOV_EXPERIMENTAL_IMAGE_REFERENCING", "False")):
            # experimental flag on running image referencers
            return report
        if not files and not root_folder:
            logging.debug("No resources to scan.")
            return report
        if files:
            for file in files:
                self.iterate_image_files(file, report, runner_filter)

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
                    image_report = self.get_image_report(dockerfile_path=abs_fname, image_id=image,
                                                         runner_filter=runner_filter)
                    merge_reports(report, image_report)

    def get_image_report(self, dockerfile_path: str, image_id: str, runner_filter: RunnerFilter) -> Report:
        """

        :param dockerfile_path: path of a file that might contain a container image
        :param image_id: sha of an image
        :param runner_filter:
        :return: vulnerability report
        """
        report = Report(self.check_type)

        scan_result = self.scan(image_id, dockerfile_path, runner_filter)
        if scan_result is None:
            return report
        self.raw_report = scan_result
        result = scan_result.get('results', [{}])[0]
        vulnerabilities = result.get("vulnerabilities") or []
        self.parse_vulns_to_records(report, result, f"{dockerfile_path} ({image_id})", runner_filter, vulnerabilities,
                                    file_abs_path=os.path.abspath(dockerfile_path))
        return report
