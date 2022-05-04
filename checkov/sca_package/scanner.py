import asyncio
import json
import logging
import os
import time
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Dict, Any

import requests

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.file_utils import compress_file_gzip_base64, decompress_file_gzip_base64
from checkov.common.util.http_utils import request_wrapper

SLEEP_DURATION = 2
MAX_SLEEP_DURATION = 60


class Scanner:
    def __init__(self) -> None:
        self._base_url = bc_integration.api_url

    def scan(self, input_paths: "Iterable[Path]") \
            -> "Sequence[Dict[str, Any]]":
        scan_results = asyncio.run(
            self.run_scan_multi(input_paths=input_paths)
        )
        return scan_results

    async def run_scan_multi(
            self,
            input_paths: "Iterable[Path]",
    ) -> "Sequence[Dict[str, Any]]":

        if os.getenv("PYCHARM_HOSTED") == "1":
            # PYCHARM_HOSTED env variable equals 1 when running via Pycharm.
            # it avoids us from crashing, which happens when using multiprocessing via Pycharm's debug-mode
            logging.warning("Running the scans in sequence for avoiding crashing when running via Pycharm")
            scan_results = []
            for input_path in input_paths:
                scan_results.append(await self.run_scan(input_path))
        else:
            scan_results = await asyncio.gather(*[self.run_scan(i) for i in input_paths])

        return scan_results

    async def run_scan(self, input_path: Path) -> dict:
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
            return self.parse_api_result(input_path, response_json["outputData"])

        return self.run_scan_busy_wait(input_path, response_json['id'])

    def run_scan_busy_wait(self, input_path: Path, scan_id: str) -> dict:
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

    def parse_api_result(self, origin_file_path: Path, response: str) -> dict:
        raw_result = json.loads(decompress_file_gzip_base64(response))
        raw_result['repository'] = str(origin_file_path)
        return raw_result
