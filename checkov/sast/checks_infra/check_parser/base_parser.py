from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from checkov.sast.consts import SemgrepAttribute, CHECKOV_SEVERITY_TO_SEMGREP_SEVERITY


class BaseSastCheckParser(ABC):
    def parse_raw_check_to_semgrep(self, raw_check: Dict[str, Dict[str, Any]], check_file: str | None = None) -> Dict[str, Any]:
        semgrep_rule: Dict[str, Any] = {}
        if not self._raw_check_is_valid(raw_check):
            logging.error(f'cant parse the following policy: {raw_check}')
        try:
            semgrep_rule = self._parse_rule_metadata(raw_check, check_file, semgrep_rule)
            check_definition = raw_check['definition']
            if raw_check.get('mode', '') == 'taint':
                semgrep_rule['mode'] = 'taint'
                semgrep_rule.update(self._parse_taint_mode_definition(check_definition))
            else:
                semgrep_rule.update(self._parse_definition(check_definition))
        except Exception as e:
            logging.error(f'the policy in file {check_file} is could not be parsed properly.\n{e}')

        return semgrep_rule

    def _raw_check_is_valid(self, raw_check: Dict[str, Any]) -> bool:
        metadata = raw_check.get('metadata')
        if not metadata:
            raise AttributeError('BQL policy is missing the metadata field')
        if not metadata.get('id'):
            raise AttributeError('BQL policy metadata is missing an id value')
        if not raw_check.get('scope', {}).get('languages'):
            raise AttributeError('BQL policy metadata is missing languages')
        else:
            return True

    def _parse_rule_metadata(self, bql_policy: Dict[str, Any], check_file: str | None, semgrep_rule: Dict[str, Any]) \
            -> Dict[str, Any]:
        metadata = bql_policy['metadata']
        semgrep_rule[str(SemgrepAttribute.ID)] = metadata['id']
        semgrep_rule[str(SemgrepAttribute.MESSAGE)] = metadata.get('guidelines', '')

        languages = bql_policy['scope']['languages']
        semgrep_rule[str(SemgrepAttribute.LANGUAGES)] = languages
        metadata_obj = {
            'name': metadata['name']
        }
        # add optional metadata fields
        semgrep_rule[str(SemgrepAttribute.SEVERITY)] = CHECKOV_SEVERITY_TO_SEMGREP_SEVERITY[metadata.get('severity', 'MEDIUM')]
        if check_file:
            metadata_obj['check_file'] = check_file
        cwe = metadata.get('cwe')
        if cwe:
            metadata_obj[SemgrepAttribute.CWE.value] = cwe
        owasp = metadata.get('owasp')
        if owasp:
            metadata_obj[SemgrepAttribute.OWASP.value] = owasp
        semgrep_rule['metadata'] = metadata_obj
        return semgrep_rule

    @abstractmethod
    def _parse_definition(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _parse_taint_mode_definition(self, definitions: Dict[str, Any]) -> Dict[str, Any]:
        pass
