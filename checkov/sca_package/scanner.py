import asyncio
import logging
import os
import time
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Dict, Any

import requests
from aiomultiprocess import Pool

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.common.util.file_utils import compress_file_gzip_base64, decompress_file_gzip_base64
from checkov.common.util.http_utils import get_default_get_headers


class Scanner:
    def __init__(self) -> None:
        self.base_url = bc_integration.api_url
        self.headers = merge_dicts(
            get_default_get_headers(bc_integration.bc_source, bc_integration.bc_source_version),
            {"Authorization": bc_integration.get_auth_token()},
        )

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
            input_paths = [(input_path,) for input_path in input_paths]
            async with Pool() as pool:
                scan_results = await pool.starmap(self.run_scan, input_paths)

        return scan_results

    async def run_scan(self, input_path: Path):
        logging.info(f"Start to scan package file {input_path}")

        request_body = {
            "compressedFileBody": compress_file_gzip_base64(str(input_path)),
            "compressionMethod": "gzip",
            "fileName": input_path.name
        }

        response = requests.request(
            "POST", f"{self.base_url}/v1/api/v1/vulnerabilities/scan", headers=self.headers,
            data=request_body
        )

        response.raise_for_status()
        response_json = response.json()

        if response_json["status"] == "exists":
            response = requests.request(
                "GET", f"{self.base_url}/v1/api/v1/vulnerabilities/scan-results/{response_json['id']}",
                headers=self.headers
            )
            response_json = response.json()

            if response_json["outputType"] == "Error":
                logging.error(response_json["outputData"])
            elif response_json["outputType"] == "Result":
                return decompress_file_gzip_base64(response_json["outputData"])

        return self.run_scan_busy_wait(response_json['id'])

    def run_scan_busy_wait(self, scan_id):
        current_state = "Empty"
        desired_state = "Result"

        response = requests.Response()

        while current_state != desired_state:
            time.sleep(2)
            response = requests.request(
                "GET", f"{self.base_url}/v1/api/v1/vulnerabilities/scan-results/{scan_id}",
                headers=self.headers
            )
            response_json = response.json()
            current_state = response_json["outputType"]

            if current_state == "Error":
                logging.error(response_json["outputData"])

        return decompress_file_gzip_base64(response.json()["outputData"])
