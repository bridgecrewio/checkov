from __future__ import annotations

import logging
from typing import Dict, Any, List

from checkov.common.graph.checks_infra.enums import Operators
from checkov.sast.consts import COMPARISON_VALUES, COMPARISON_VALUE_TO_SYMBOL, SemgrepAttribute, \
    CHECKOV_SEVERITY_TO_SEMGREP_SEVERITY, PATTERN_OPERATOR_TO_SEMGREP_ATTR, VARIABLE_OPERATOR_TO_SEMGREP_ATTR, \
    FILTER_OPERATOR_TO_SEMGREP_ATTR, BqlConditionType
from checkov.common.util.type_forcers import force_list


class SastCheckParser:
    def parse_raw_check_to_semgrep(self, raw_check: Dict[str, Dict[str, Any]], check_file: str | None = None) -> Dict[str, Any]:
        semgrep_rule: Dict[str, Any] = {}
        if not self._raw_check_is_valid(raw_check):
            logging.error(f'cant parse the following policy: {raw_check}')
        try:
            semgrep_rule = self._parse_rule_metadata(raw_check, check_file, semgrep_rule)
            semgrep_rule.update(self._parse_definition(raw_check['definition']))
        except Exception as e:
            logging.error(f'the policy in file {check_file} is misconfigured so it could not be parsed properly.\n{e}')

        return semgrep_rule

    def _raw_check_is_valid(self, raw_check: Dict[str, Any]) -> bool:
        metadata = raw_check.get('metadata')
        if not metadata:
            raise AttributeError('BQL policy is missing the metadata field')
        if not metadata.get('id'):
            raise AttributeError('BQL policy metadata is missing an id value')
        if not metadata.get('severity'):
            raise AttributeError('BQL policy metadata is missing a severity')
        if not raw_check.get('scope', {}).get('languages'):
            raise AttributeError('BQL policy metadata is missing languages')
        else:
            return True

    def _parse_rule_metadata(self, bql_policy: Dict[str, Any], check_file, semgrep_rule: Dict[str, Any]) \
            -> Dict[str, Any]:
        metadata = bql_policy['metadata']
        semgrep_rule[str(SemgrepAttribute.ID)] = metadata['id']
        semgrep_rule[str(SemgrepAttribute.MESSAGE)] = metadata.get('guidelines', '')
        semgrep_rule[str(SemgrepAttribute.SEVERITY)] = CHECKOV_SEVERITY_TO_SEMGREP_SEVERITY[metadata['severity']]
        languages = bql_policy['scope']['languages']
        semgrep_rule[str(SemgrepAttribute.LANGUAGES)] = languages
        metadata_obj = {
            'name': metadata['name']
        }
        # add optional metadata fields
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

    def _parse_definition(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        definitions = force_list(definition)
        conf = {}
        if len(definitions) > 1:
            return {str(SemgrepAttribute.PATTERNS): self._get_definitions_list_items(definitions)}
        elif len(definitions) == 1:
            definition = definitions[0]
            if not isinstance(definition, dict):
                raise TypeError(f'bad definition type, got {type(definition)} instead of dict')
            if definition.get(str(BqlConditionType.OR)):
                return {str(SemgrepAttribute.PATTERN_EITHER): self._get_definitions_list_items(
                    definition[str(BqlConditionType.OR)])}
            elif definition.get(str(BqlConditionType.AND)):
                return {str(SemgrepAttribute.PATTERNS): self._get_definitions_list_items(
                    definition[str(BqlConditionType.AND)])}
            else:
                return self._parse_single_definition(definition)
        return conf

    def _parse_single_definition(self, definition: Dict[str, Any]):
        cond_type = definition.get('cond_type', '')
        if not cond_type:
            raise AttributeError('BQL policy is missing a condition type')
        operator = definition.get('operator', '')
        if not operator:
            raise AttributeError(f'BQL policy condition type: {cond_type} is missing an operator')
        definition_value = definition.get('value')
        if not definition_value:
            raise AttributeError(f'BQL policy condition type: {cond_type} is missing a definition value')

        if cond_type == BqlConditionType.PATTERN:
            return self._parse_pattern_cond_type(operator, definition_value)

        elif cond_type == BqlConditionType.VARIABLE:
            return self._parse_variable_cond_type(operator, definition, definition_value)

        elif cond_type == BqlConditionType.FILTER:
            return self._parse_filter_cond_type(operator, definition_value)

    def _parse_pattern_cond_type(self, operator, definition_value):
        semgrep_attr = PATTERN_OPERATOR_TO_SEMGREP_ATTR.get(operator, '')
        if not semgrep_attr:
            raise AttributeError(f'BQL policy pattern condition contains an unknown operator: {operator}')
        return {semgrep_attr: definition_value}

    def _parse_variable_cond_type(self, operator, definition, definition_value):
        metavariable_condition_object = {}
        metavariable = definition.get('variable')
        metavariable_condition_object[SemgrepAttribute.METAVARIABLE.value] = metavariable
        metavariable_condition_key = VARIABLE_OPERATOR_TO_SEMGREP_ATTR.get(operator, '')
        if not metavariable_condition_key:
            raise AttributeError(f'BQL policy variable condition contains an unknown operator: {operator}')

        if operator == Operators.REGEX_MATCH:
            metavariable_condition_object[SemgrepAttribute.REGEX.value] = definition_value

        elif operator == Operators.PATTERN_MATCH:
            if isinstance(definition_value, str):
                metavariable_condition_object[SemgrepAttribute.PATTERN.value] = definition_value
            else:
                metavariable_condition = self._parse_definition(definition_value)
                metavariable_condition_object.update(metavariable_condition)

        elif operator in COMPARISON_VALUES:
            metavariable_condition_object[
                SemgrepAttribute.COMPARISON.value] = f'{metavariable} {COMPARISON_VALUE_TO_SYMBOL[operator]} {definition_value}'

        return {metavariable_condition_key: metavariable_condition_object}

    def _parse_filter_cond_type(self, operator, definition_value):
        semgrep_attr = FILTER_OPERATOR_TO_SEMGREP_ATTR.get(operator, '')
        if not semgrep_attr:
            raise AttributeError(f'BQL filter condition contains an unknown operator: {operator}')
        return {semgrep_attr: definition_value}

    def _get_definitions_list_items(self, definitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        conf = []
        for definition in definitions:
            if definition.get(str(BqlConditionType.OR)):
                conf.append({SemgrepAttribute.PATTERN_EITHER.value: self._get_definitions_list_items(
                    definition[str(BqlConditionType.OR)])})
            elif definition.get(str(BqlConditionType.AND)):
                conf.append({SemgrepAttribute.PATTERNS.value: self._get_definitions_list_items(
                    definition[str(BqlConditionType.AND)])})
            else:
                conf.append(self._parse_definition(definition))

        return conf
