from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from checkov.common.bridgecrew.platform_integration import bc_integration

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

    def scan(self) -> Sequence[dict[str, Any]]:
        """run SCA package scan and poll scan results"""
        pass

    def run_scan(self) -> dict[str, Any]:
        pass

    def poll_scan_result(self) -> dict[str, Any]:
        pass
