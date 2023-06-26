from __future__ import annotations

from typing import Dict, Any, List

from checkov.common.graph.checks_infra.enums import Operators
from checkov.sast.consts import COMPARISON_VALUES, COMPARISON_VALUE_TO_SYMBOL, SemgrepAttribute, \
    PATTERN_OPERATOR_TO_SEMGREP_ATTR, VARIABLE_OPERATOR_TO_SEMGREP_ATTR, \
    FILTER_OPERATOR_TO_SEMGREP_ATTR, BqlV1ConditionType
from checkov.sast.checks_infra.check_parser.base_parser import BaseSastCheckParser
from checkov.common.util.type_forcers import force_list


class SastCheckParserV01(BaseSastCheckParser):
    def _parse_definition(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        definitions = force_list(definition)
        conf: Dict[str, Any] = {}
        if len(definitions) > 1:
            return {str(SemgrepAttribute.PATTERNS): self._get_definitions_list_items(definitions)}
        elif len(definitions) == 1:
            definition = definitions[0]
            if not isinstance(definition, dict):
                raise TypeError(f'bad definition type, got {type(definition)} instead of dict')
            if definition.get(str(BqlV1ConditionType.OR)):
                return {str(SemgrepAttribute.PATTERN_EITHER): self._get_definitions_list_items(
                    definition[str(BqlV1ConditionType.OR)])}
            elif definition.get(str(BqlV1ConditionType.AND)):
                return {str(SemgrepAttribute.PATTERNS): self._get_definitions_list_items(
                    definition[str(BqlV1ConditionType.AND)])}
            else:
                return self._parse_single_definition(definition)
        return conf

    def _parse_single_definition(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        cond_type = definition.get('cond_type', '')
        if not cond_type:
            raise AttributeError('BQL policy is missing a condition type')
        operator = definition.get('operator', '')
        if not operator:
            raise AttributeError(f'BQL policy condition type: {cond_type} is missing an operator')
        definition_value = definition.get('value')
        if not definition_value:
            raise AttributeError(f'BQL policy condition type: {cond_type} is missing a definition value')

        if cond_type == BqlV1ConditionType.PATTERN:
            return self._parse_pattern_cond_type(operator, definition_value)

        elif cond_type == BqlV1ConditionType.VARIABLE:
            return self._parse_variable_cond_type(operator, definition, definition_value)

        elif cond_type == BqlV1ConditionType.FILTER:
            return self._parse_filter_cond_type(operator, definition_value)

        elif cond_type in [BqlV1ConditionType.PATTERN_SINK, BqlV1ConditionType.PATTERN_SANITIZER, BqlV1ConditionType.PATTERN_SOURCE]:
            return self._parse_taint_cond_type(operator, definition_value)

        return {}

    def _parse_pattern_cond_type(self, operator: str, definition_value: str) -> Dict[str, Any]:
        semgrep_attr = PATTERN_OPERATOR_TO_SEMGREP_ATTR.get(operator, '')
        if not semgrep_attr:
            raise AttributeError(f'BQL policy pattern condition contains an unknown operator: {operator}')
        return {semgrep_attr: definition_value}

    def _parse_variable_cond_type(self, operator: str, definition: Dict[str, Any],
                                  definition_value: str | Dict[str, Any]) -> Dict[str, Any]:
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

    def _parse_filter_cond_type(self, operator: str, definition_value: str | Dict[str, Any]) -> Dict[str, Any]:
        semgrep_attr = FILTER_OPERATOR_TO_SEMGREP_ATTR.get(operator, '')
        if not semgrep_attr:
            raise AttributeError(f'BQL filter condition contains an unknown operator: {operator}')
        return {semgrep_attr: definition_value}

    def _parse_taint_cond_type(self, operator: str, definition_value: str | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(definition_value, dict) and (definition_value.get(BqlV1ConditionType.AND) or definition_value.get(BqlV1ConditionType.OR)):
            return self._parse_definition(definition_value)
        else:
            if not isinstance(definition_value, str):
                raise ValueError(f'unexpected definition value: {definition_value}')
            return self._parse_pattern_cond_type(operator, definition_value)

    def _get_definitions_list_items(self, definitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        conf = []
        for definition in definitions:
            if definition.get(str(BqlV1ConditionType.OR)):
                conf.append({SemgrepAttribute.PATTERN_EITHER.value: self._get_definitions_list_items(
                    definition[str(BqlV1ConditionType.OR)])})
            elif definition.get(str(BqlV1ConditionType.AND)):
                conf.append({SemgrepAttribute.PATTERNS.value: self._get_definitions_list_items(
                    definition[str(BqlV1ConditionType.AND)])})
            else:
                conf.append(self._parse_definition(definition))

        return conf

    def _parse_taint_mode_definition(self, definitions: Dict[str, Any]) -> Dict[str, Any]:
        conf: Dict[str, Any] = {
            str(SemgrepAttribute.PATTERN_SOURCES): [],
            str(SemgrepAttribute.PATTERN_SINKS): []
        }
        if not isinstance(definitions, list):
            raise TypeError(f'bad taint mode definition type, got {type(definitions)} instead of list')
        for definition in definitions:
            cond_type = definition.get('cond_type', '')
            if not cond_type:
                raise AttributeError('BQL policy is missing a condition type')
            operator = definition.get('operator', '')
            if not operator:
                raise AttributeError(f'BQL policy condition type: {cond_type} is missing an operator')
            definition_value = definition.get('value')
            if not definition_value:
                raise AttributeError(f'BQL policy condition type: {cond_type} is missing a definition value')

            if cond_type == BqlV1ConditionType.PATTERN_SOURCE:
                conf[str(SemgrepAttribute.PATTERN_SOURCES)].append(self._parse_definition(definition))
            elif cond_type == BqlV1ConditionType.PATTERN_SINK:
                conf[str(SemgrepAttribute.PATTERN_SINKS)].append(self._parse_definition(definition))
            elif cond_type == BqlV1ConditionType.PATTERN_SANITIZER:
                conf.setdefault(str(SemgrepAttribute.PATTERN_SANITIZERS), []).append(self._parse_definition(definition))
            elif cond_type == BqlV1ConditionType.PATTERN_PROPAGATOR:
                conf.setdefault(str(SemgrepAttribute.PATTERN_PROPAGATORS), []).append(self._parse_definition(definition))
            else:
                raise AttributeError(f'BQL policy taint mode definition contains an unexpected condition type: {cond_type}')

        return conf
