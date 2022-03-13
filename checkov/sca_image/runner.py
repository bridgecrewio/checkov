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
from checkov.common.output.report import Report, CheckType
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.runner import Runner as PackageRunner


class Runner(PackageRunner):
    check_type = CheckType.SCA_IMAGE

    def __init__(self) -> None:
        self._check_class: Optional[str] = None
        self._code_repo_path: Optional[Path] = None
        self._check_class = f"{image_scanner.__module__}.{image_scanner.__class__.__qualname__}"
        self.raw_report: Optional[Dict[str, Any]] = None

    def scan(
            self,
            image_id: str,
            dockerfile_path: str,
            runner_filter: RunnerFilter = RunnerFilter(),
    ) -> Optional[Dict[str, Any]]:

        # skip complete run, if flag '--check' was used without a CVE check ID
        if runner_filter.checks and all(not check.startswith("CKV_CVE") for check in runner_filter.checks):
            return None

        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SCA package scanning")
            return None

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

        dockerfile_path = kwargs['dockerfile_path']
        image_id = kwargs['image_id']
        scan_result = self.scan(image_id, dockerfile_path, runner_filter)
        if scan_result is None:
            return report
        self.raw_report = scan_result
        result = scan_result.get('results', [{}])[0]

        vulnerabilities = result.get("vulnerabilities") or []
        self.parse_vulns_to_records(report, result, f"{dockerfile_path} ({image_id})", runner_filter, vulnerabilities,
                                    file_abs_path=os.path.abspath(dockerfile_path))

        return report
