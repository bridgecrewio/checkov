from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections.abc import Iterable, Sequence, Collection
from pathlib import Path
from typing import Dict, Any, List

import requests

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.platform_key import bridgecrew_dir
from checkov.common.bridgecrew.vulnerability_scanning.image_scanner import image_scanner, TWISTCLI_FILE_NAME
from checkov.common.bridgecrew.vulnerability_scanning.integrations.docker_image_scanning import \
    docker_image_scanning_integration
from checkov.common.util.file_utils import compress_file_gzip_base64, decompress_file_gzip_base64
from checkov.common.util.http_utils import request_wrapper

from checkov.common.util.tqdm_utils import ProgressBar

SLEEP_DURATION = 2
MAX_SLEEP_DURATION = 60


class Scanner:
    def __init__(self, pbar: ProgressBar | None = None, root_folder: str | Path | None = None) -> None:
        self._base_url = bc_integration.api_url
        if pbar:
            self.pbar = pbar
        else:
            self.pbar = ProgressBar('')
            self.pbar.turn_off_progress_bar()
        self.root_folder = root_folder

    @staticmethod
    def should_rescan_for_result(scan_result: dict[str, Any] | None) -> bool:
        return scan_result is None or scan_result.get("packages") is None

    def scan(self, input_paths: Collection[Path]) -> Sequence[dict[str, Any]] | None:
        self.pbar.initiate(len(input_paths))
        scan_results = asyncio.run(
            self.run_scan_multi(input_paths=input_paths)
        )
        self.pbar.close()
        return scan_results

    async def run_scan_multi(
            self,
            input_paths: "Iterable[Path]",
    ) -> "Sequence[Dict[str, Any]] | None":

        if os.getenv("PYCHARM_HOSTED") == "1":
            # PYCHARM_HOSTED env variable equals 1 when running via Pycharm.
            # it avoids us from crashing, which happens when using multiprocessing via Pycharm's debug-mode
            logging.warning("Running the scans in sequence for avoiding crashing when running via Pycharm")
            scan_results: list[dict[str, Any] | None] = []
            for input_path in input_paths:
                scan_results.append(await self.run_scan(input_path))
        else:
            scan_results = await asyncio.gather(*[self.run_scan(i) for i in input_paths])

        if any(self.should_rescan_for_result(scan_result) for scan_result in scan_results):
            status: bool = image_scanner.setup_twistcli()

            if not status:
                return None
            if os.getenv("PYCHARM_HOSTED") == "1":
                # PYCHARM_HOSTED env variable equals 1 when running via Pycharm.
                # it avoids us from crashing, which happens when using multiprocessing via Pycharm's debug-mode
                logging.warning("Running the scans in sequence for avoiding crashing when running via Pycharm")
                scan_results = [
                    await self.execute_twistcli_scan(input_path) if self.should_rescan_for_result(scan_results[idx])
                    else scan_results[idx] for idx, input_path in enumerate(input_paths)
                ]
            else:
                input_paths_as_list: List[Path] = list(input_paths)  # create a list from a set ("Iterable")
                indices_to_fix: List[int] = [
                    idx
                    for idx in range(len(input_paths_as_list))
                    if self.should_rescan_for_result(scan_results[idx])
                ]
                new_scan_results = await asyncio.gather(*[
                    self.execute_twistcli_scan(input_paths_as_list[idx]) for idx in indices_to_fix
                ])
                for idx in indices_to_fix:
                    res = new_scan_results.pop(0)
                    res['repository'] = str(input_paths_as_list[idx])
                    scan_results[idx] = res

        # checking whether there are None results that indicates for error. id there is any, we return None
        scan_results_without_nones: list[dict[str, Any]] = []
        for result in scan_results:
            if result is None:
                return None
            else:
                scan_results_without_nones.append(result)

        return scan_results_without_nones

    async def run_scan(self, input_path: Path) -> dict[str, Any] | None:
        try:
            self.pbar.set_additional_data({'Current File Scanned': os.path.relpath(input_path, self.root_folder)})
            logging.info(f"Start to scan package file {input_path}")

            request_body = {
                "compressedFileBody": compress_file_gzip_base64(str(input_path)),
                "compressionMethod": "gzip",
                "fileName": input_path.name
            }

            response = request_wrapper(
                "POST", f"{self._base_url}/api/v1/vulnerabilities/scan",
                headers=bc_integration.get_default_headers("POST"),
                json=request_body,
                should_call_raise_for_status=True
            )

            response_json = response.json()

            if response_json["status"] == "already_exist":
                logging.info(f"result for {input_path} exists in the cache")
                return self.parse_api_result(input_path, response_json["outputData"])

            return self.run_scan_busy_wait(input_path, response_json['id'])
        except Exception:
            logging.debug(
                "[sca_package] - Unexpected failure happened during package scanning.\n"
                "the scanning is terminating. details are below.\n"
                "please try again. if it is repeated, please report.", exc_info=True)
            return None

    def run_scan_busy_wait(self, input_path: Path, scan_id: str) -> dict[str, Any]:
        current_state = "Empty"
        desired_state = "Result"
        total_sleeping_time = 0
        response = requests.Response()

        while current_state != desired_state:
            response = request_wrapper(
                "GET", f"{self._base_url}/api/v1/vulnerabilities/scan-results/{scan_id}",
                headers=bc_integration.get_default_headers("GET")
            )
            response_json = response.json()
            current_state = response_json["outputType"]

            if current_state == "Error":
                logging.error(response_json["outputData"])
                return {}

            if total_sleeping_time > MAX_SLEEP_DURATION:
                logging.info(f"Timeout, slept for {total_sleeping_time}")
                return {}

            time.sleep(SLEEP_DURATION)
            total_sleeping_time += SLEEP_DURATION

        return self.parse_api_result(input_path, response.json()["outputData"])

    def parse_api_result(self, origin_file_path: Path, response: str) -> dict[str, Any]:
        raw_result: dict[str, Any] = json.loads(decompress_file_gzip_base64(response))
        raw_result['repository'] = str(origin_file_path)
        self.pbar.update()
        return raw_result

    async def execute_twistcli_scan(
            self,
            input_path: Path,
    ) -> Dict[str, Any]:
        output_path = Path(f'results-{input_path.name}.json')

        command = f"{Path(bridgecrew_dir) / TWISTCLI_FILE_NAME} coderepo scan --address {docker_image_scanning_integration.get_proxy_address()} --token {docker_image_scanning_integration.get_bc_api_key()} --details --output-file \"{output_path}\" {input_path}"
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
        output_path.unlink()
        return scan_result
