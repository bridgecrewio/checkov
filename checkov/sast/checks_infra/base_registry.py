from __future__ import annotations

import logging
import os

from typing import List, Any, Optional, Dict

from checkov.common.bridgecrew.check_type import CheckType

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.runner_filter import RunnerFilter

logger = logging.getLogger(__name__)


class Registry(BaseCheckRegistry):
    def __init__(self, checks_dir: str | None = None) -> None:
        super().__init__(report_type=CheckType.SAST)
        self.rules: List[Dict[str, Any]] = []
        self.checks_dir = checks_dir
        self.logger = logging.getLogger(__name__)
        self.runner_filter: Optional[RunnerFilter] = None
        self.checks_dirs_path: List[str] = [checks_dir] if checks_dir else []

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        # TODO
        return '', '', {}

    def set_runner_filter(self, runner_filter: RunnerFilter) -> None:
        self.runner_filter = runner_filter

    def add_external_dirs(self, external_dirs: Optional[List[str]]) -> None:
        if external_dirs:
            for path in external_dirs:
                if os.path.exists(path):
                    if not os.path.isabs(path):
                        path = os.path.abspath(path)
                    self.checks_dirs_path.append(path)
                else:
                    logger.warning(f"path: {path} not found")
