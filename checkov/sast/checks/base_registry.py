from __future__ import annotations

import logging
import os
import yaml
from typing import List, Any, Optional, Set, Dict
from checkov.common.bridgecrew.check_type import CheckType
from checkov.sast.checks.base_check import BaseSastCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.runner_filter import RunnerFilter
from checkov.sast.consts import SastLanguages
from checkov.common.checks_infra.registry import CHECKS_POSSIBLE_ENDING


class Registry(BaseCheckRegistry):
    def __init__(self, checks_dir: str) -> None:
        super().__init__(report_type=CheckType.SAST)
        self.rules: List[str] = []
        self.checks_dir = checks_dir
        self.logger = logging.getLogger(__name__)
        self.runner_filter: Optional[RunnerFilter] = None

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        # TODO
        return '', '', {}

    def set_runner_filter(self, runner_filter: RunnerFilter) -> None:
        self.runner_filter = runner_filter

    def load_rules(self, sast_languages: Optional[Set[SastLanguages]]) -> None:
        if sast_languages:
            self._load_checks_from_dir(self.checks_dir, sast_languages)

    def load_external_rules(self, dir: str, sast_languages: Optional[Set[SastLanguages]]) -> None:
        if sast_languages:
            self._load_checks_from_dir(dir, sast_languages)

    def _load_checks_from_dir(self, directory: str, sast_languages: Set[SastLanguages]) -> None:
        dir = os.path.expanduser(directory)
        self.logger.debug(f'Loading external checks from {dir}')
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
                        if self._should_skip_check(rule):
                            break
                        for lang in rule.get('languages', []):
                            if lang in [lan.value for lan in sast_languages]:
                                checks.add(os.path.join(root, file))
                                break
        self.rules += list(checks)

    @staticmethod
    def _get_check_from_rule(rule: Dict[str, Any]) -> Optional[BaseSastCheck]:
        name = rule.get('metadata', {}).get('name', '')
        id = rule.get('id', '')
        if not name or not id:
            logging.warning('Sast check has no name or ID')
            return None
        check = BaseSastCheck(name, id)
        return check

    def _should_skip_check(self, rule: Dict[str, Any]) -> bool:
        if not self.runner_filter:
            return False
        check = Registry._get_check_from_rule(rule)
        if not check:
            return True
        if self.runner_filter.should_run_check(check):
            return False
        return True
