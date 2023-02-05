from __future__ import annotations

import logging
import os
import yaml
from typing import List
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.sast.enums import SastLanguages

CHECKS_POSSIBLE_ENDING = [".yaml", ".yml"]


class Registry(BaseCheckRegistry):
    def __init__(self, checks_dir: str) -> None:
        super().__init__(report_type=CheckType.SAST)
        self.checks: List[str] = []
        self.checks_dir = checks_dir
        self.logger = logging.getLogger(__name__)

    def load_checks(self, sast_languages: List[SastLanguages]) -> None:
        self._load_checks_from_dir(self.checks_dir, sast_languages)

    def load_external_checks(self, dir: str, sast_languages: List[SastLanguages]) -> None:
        self._load_checks_from_dir(dir, sast_languages)

    def _load_checks_from_dir(self, directory: str, sast_languages: List[SastLanguages]) -> None:
        dir = os.path.expanduser(directory)
        self.logger.debug("Loading external checks from {}".format(dir))
        checks = set()
        for root, d_names, f_names in os.walk(dir):
            self.logger.debug(f"Searching through {d_names} and {f_names}")
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending not in CHECKS_POSSIBLE_ENDING:
                    continue
                with open(os.path.join(root, file), "r") as f:
                    try:
                        rules = yaml.safe_load(f).get('rules', [])
                    except Exception:
                        logging.warning(f'cant parse rule file {file}')
                        continue
                    for rule in rules:
                        for lang in rule.get('languages', []):
                            if lang in [lan.value for lan in sast_languages]:
                                checks.add(os.path.join(root, file))
                                break
        self.checks += list(checks)
