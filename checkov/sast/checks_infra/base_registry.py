from __future__ import annotations

import logging
import os

import yaml
from typing import List, Any, Optional, Set, Dict, Iterable

from checkov.common.bridgecrew.check_type import CheckType
from checkov.sast.checks_infra.base_check import BaseSastCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.runner_filter import RunnerFilter
from checkov.sast.checks_infra.checks_parser import SastCheckParser
from checkov.sast.consts import SastLanguages
from checkov.common.checks_infra.registry import CHECKS_POSSIBLE_ENDING


class Registry(BaseCheckRegistry):
    def __init__(self, checks_dir: str, temp_semgrep_rules_path: str | None = None) -> None:
        super().__init__(report_type=CheckType.SAST)
        self.rules: List[Dict[str, Any]] = []
        self.checks_dir = checks_dir
        self.logger = logging.getLogger(__name__)
        self.parser = SastCheckParser()
        self.runner_filter: Optional[RunnerFilter] = None
        self.temp_semgrep_rules_path = temp_semgrep_rules_path if temp_semgrep_rules_path else \
            os.path.join(self.checks_dir, 'temp_semgrep_rules.yaml')

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        # TODO
        return '', '', {}

    def set_runner_filter(self, runner_filter: RunnerFilter) -> None:
        self.runner_filter = runner_filter

    def load_rules(self, frameworks: Iterable[str], sast_languages: Optional[Set[SastLanguages]]) -> int:
        actual_sast_languages = sast_languages if 'all' not in frameworks else SastLanguages.set()
        if actual_sast_languages:
            return self._load_checks_from_dir(self.checks_dir, actual_sast_languages)
        return 0

    def load_external_rules(self, dir: str, sast_languages: Optional[Set[SastLanguages]]) -> int:
        if sast_languages:
            return self._load_checks_from_dir(dir, sast_languages)
        return 0

    def _load_checks_from_dir(self, directory: str, sast_languages: Set[SastLanguages]) -> int:
        dir = os.path.expanduser(directory)
        self.logger.debug(f'Loading external checks from {dir}')
        rules = {}  # constructed as a dict of {rule_id: rule_object} to avoid duplications
        for root, d_names, f_names in os.walk(dir):
            self.logger.debug(f"Searching through {d_names} and {f_names}")
            for file in f_names:
                file_ending = os.path.splitext(file)[1]
                if file_ending not in CHECKS_POSSIBLE_ENDING:
                    continue
                with open(os.path.join(root, file), "r") as f:
                    try:
                        raw_check = yaml.safe_load(f)
                        parsed_rule = self.parser.parse_raw_check_to_semgrep(raw_check, str(file))
                    except Exception as e:
                        logging.warning(f'Cannot parse rule file {file} due to: {e}')
                        continue
                    if self._should_skip_check(parsed_rule):
                        continue
                    for lang in parsed_rule.get('languages', []):
                        if lang in [lan.value for lan in sast_languages]:
                            rules[parsed_rule['id']] = parsed_rule
                            break
        self.rules += rules.values()
        return len(self.rules)

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

    def create_temp_rules_file(self) -> None:
        rules_obj = {'rules': self.rules}
        with open(self.temp_semgrep_rules_path, 'w') as tempfile:
            yaml.safe_dump(rules_obj, tempfile)
        logging.debug(f'created semgrep temporary rules file at: {self.temp_semgrep_rules_path}')

    def delete_temp_rules_file(self) -> None:
        try:
            os.remove(self.temp_semgrep_rules_path)
            logging.debug('deleted semgrep temporary rules file')
        except FileNotFoundError as e:
            logging.error(f'Tried to delete the semgrep temporary rules file but no such file was found.\n{e}')
