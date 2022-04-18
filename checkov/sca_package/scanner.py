import asyncio
import json
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
from checkov.common.util.http_utils import get_default_get_headers, get_default_post_headers


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
                scan_results.append(self.run_scan(input_path))
        else:
            input_paths = [(input_path,) for input_path in input_paths]
            with Pool() as pool:
                scan_results = pool.starmap(self.run_scan, input_paths)

        return scan_results

    def run_scan(self, input_path: Path) -> dict:
        logging.info(f"Start to scan package file {input_path}")

        headers = merge_dicts(
            get_default_get_headers(bc_integration.bc_source, bc_integration.bc_source_version),
            {"Authorization": bc_integration.get_auth_token()},
        )

        request_body = {
            "compressedFileBody": compress_file_gzip_base64(str(input_path)),
            "compressionMethod": "gzip",
            "fileName": input_path.name
        }

        response = requests.request(
            "POST", f"{self.base_url}/api/v1/vulnerabilities/scan", headers=headers,
            data=request_body
        )

        response.raise_for_status()
        response_json = response.json()

        if response_json["status"] == "already_exist":
            return json.loads(
                decompress_file_gzip_base64(
                    response_json["outputData"]
                )
            )

        return self.run_scan_busy_wait(response_json['id'])

    def run_scan_busy_wait(self, scan_id: str) -> dict:
        current_state = "Empty"
        desired_state = "Result"

        headers = merge_dicts(
            get_default_get_headers(bc_integration.bc_source, bc_integration.bc_source_version),
            {"Authorization": bc_integration.get_auth_token()},
        )
        response = requests.Response()

        while current_state != desired_state:
            response = requests.request(
                "GET", f"{self.base_url}/api/v1/vulnerabilities/scan-results/{scan_id}",
                headers=headers
            )
            response_json = response.json()
            current_state = response_json["outputType"]

            if current_state == "Error":
                logging.error(response_json["outputData"])
                return {}

            time.sleep(2)

        return json.loads(
                decompress_file_gzip_base64(
                    response.json()["outputData"]
                    )
                )
