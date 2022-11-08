from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from checkov.common.util.http_utils import request_wrapper

from checkov.common.bridgecrew.platform_integration import bc_integration

from checkov.common.util.tqdm_utils import ProgressBar

SLEEP_DURATION = 2
MAX_SLEEP_DURATION = 60


class Scanner:
    def __init__(self, pbar: ProgressBar | None = None, root_folder: str | Path | None = None) -> None:
        self._base_url = bc_integration.api_url
        self.bc_cli_scan_api_url = f"{self._base_url}/api/v1/vulnerabilities/cli/scan"
        if pbar:
            self.pbar = pbar
        else:
            self.pbar = ProgressBar('')
            self.pbar.turn_off_progress_bar()
        self.root_folder = root_folder

    def scan(self) -> Sequence[dict[str, Any]] | None:
        """run SCA package scan and poll scan results"""
        if not self.run_scan():
            return None
        self.poll_scan_result()
        return []

    def run_scan(self) -> bool:
        logging.info("Start to scan package files.")

        request_body = {
            "branch": "",
            "commit": "",
            "path": os.path.join(bc_integration.repo_path, '') if bc_integration.repo_path else "",
            "repoId": bc_integration.repo_id,
            "id": bc_integration.timestamp,
            "repositoryId": ""
        }

        response = request_wrapper(
            "POST", self.bc_cli_scan_api_url,
            headers=bc_integration.get_default_headers("POST"),
            json=request_body,
            should_call_raise_for_status=True
        )

        response_json = response.json()

        if not response_json["startedSuccessfully"]:
            logging.info("Failed to run package scanning.")
            return False
        return True

    def poll_scan_result(self) -> dict[str, Any]:
        pass
