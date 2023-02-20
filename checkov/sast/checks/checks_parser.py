import logging
from typing import Dict, Any

from checkov.common.graph.checks_infra.enums import Operators
from checkov.sast.consts import COMPARISON_VALUES, COMPARISON_VALUE_TO_SYMBOL, SemgrepAttribute, \
    CHECKOV_SEVERITY_TO_SEMGREP_SEVERITY, PATTERN_OPERATOR_TO_SEMGREP_ATTR, VARIABLE_OPERATOR_TO_SEMGREP_ATTR, \
    FILTER_OPERATOR_TO_SEMGREP_ATTR, BqlConditionType
from checkov.common.util.type_forcers import force_list


class SastCheckParser:
    def parse_raw_check_to_semgrep(self, raw_check: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        semgrep_rule = {}
        if not self.raw_check_is_valid(raw_check):
            logging.error(f'cant parse the following policy: {raw_check}')
        try:
            semgrep_rule = self.parse_rule_metadata(raw_check, semgrep_rule)
            semgrep_rule.update(self.parse_definition(raw_check['definition']))
        except Exception as e:
            raise e

        return semgrep_rule

    def raw_check_is_valid(self, raw_check):
        metadata = raw_check.get('metadata')
        if not metadata:
            raise AttributeError(f'BQL policy is missing the metadata field')
        if not metadata.get('id'):
            raise AttributeError(f'BQL policy metadata is missing an id value')
        if not metadata.get('severity'):
            raise AttributeError(f'BQL policy metadata is missing a severity')
        if not raw_check.get('scope', {}).get('languages'):
            raise AttributeError(f'BQL policy metadata is missing languages')

        else:
            return True

    def parse_rule_metadata(self, bql_policy, semgrep_policy):
        metadata = bql_policy['metadata']
        semgrep_policy[SemgrepAttribute.ID.value] = metadata['id']
        semgrep_policy[SemgrepAttribute.MESSAGE.value] = metadata.get('guidelines', '')
        semgrep_policy[SemgrepAttribute.SEVERITY.value] = CHECKOV_SEVERITY_TO_SEMGREP_SEVERITY[metadata['severity']]
        languages = bql_policy['scope']['languages']
        semgrep_policy[SemgrepAttribute.LANGUAGES.value] = languages
        semgrep_policy['metadata'] = {'name': metadata['name']}

        # add optional cwe and owasp metadata
        cwe = metadata.get('cwe')
        if cwe:
            semgrep_policy['metadata'][SemgrepAttribute.CWE.value] = cwe
        owasp = metadata.get('owasp')
        if owasp:
            semgrep_policy['metadata'][SemgrepAttribute.OWASP.value] = owasp

        return semgrep_policy

    def parse_definition(self, definition):
        definitions = force_list(definition)
        conf = {}
        if len(definitions) > 1:
            conf[SemgrepAttribute.PATTERNS.value] = self.get_definitions_list_items(definitions)
        else:
            for definition in definitions:
                if definition.get(BqlConditionType.OR.value):
                    conf[SemgrepAttribute.PATTERN_EITHER.value] = self.get_definitions_list_items(
                        definition[BqlConditionType.OR.value])
                elif definition.get(BqlConditionType.AND.value):
                    conf[SemgrepAttribute.PATTERNS.value] = self.get_definitions_list_items(
                        definition[BqlConditionType.AND.value])
                else:
                    conf[SemgrepAttribute.PATTERNS.value] = self.get_definitions_list_items(definitions)
        return conf

    def get_definitions_list_items(self, definitions):
        conf = []
        for definition in definitions:
            # handle nested OR / AND definitions
            if definition.get(BqlConditionType.OR.value):
                conf.append({SemgrepAttribute.PATTERN_EITHER.value: self.get_definitions_list_items(
                    definition[BqlConditionType.OR.value])})
            elif definition.get(BqlConditionType.AND.value):
                conf.append({SemgrepAttribute.PATTERNS.value: self.get_definitions_list_items(
                    definition[BqlConditionType.AND.value])})

            else:
                # handle a single definition
                cond_type = definition.get('cond_type')
                operator = definition.get('operator')
                definition_value = definition.get('value')

                if cond_type == BqlConditionType.PATTERN:
                    semgrep_attr = PATTERN_OPERATOR_TO_SEMGREP_ATTR.get(operator)
                    if not semgrep_attr:
                        raise AttributeError(f'BQL policy pattern condition contains an unknown operator: {operator}')
                    conf.append({semgrep_attr: definition_value})

                elif cond_type == BqlConditionType.VARIABLE:
                    metavariable_condition_object = {}
                    metavariable = definition.get('variable')
                    metavariable_condition_object[SemgrepAttribute.METAVARIABLE.value] = metavariable
                    metavariable_condition_key = VARIABLE_OPERATOR_TO_SEMGREP_ATTR.get(operator)
                    if not metavariable_condition_key:
                        raise AttributeError(f'BQL policy variable condition contains an unknown operator: {operator}')

                    if operator == Operators.REGEX_MATCH:
                        metavariable_condition_object[SemgrepAttribute.REGEX.value] = definition_value

                    elif operator == Operators.PATTERN_MATCH:
                        metavariable_condition = self.parse_definition(definition_value)
                        metavariable_condition_object.update(metavariable_condition)

                    elif operator in COMPARISON_VALUES:
                        metavariable_condition_object[
                            SemgrepAttribute.COMPARISON.value] = f'{metavariable} {COMPARISON_VALUE_TO_SYMBOL[operator]} {definition_value}'

                    conf.append({metavariable_condition_key: metavariable_condition_object})

                elif cond_type == BqlConditionType.FILTER:
                    semgrep_attr = FILTER_OPERATOR_TO_SEMGREP_ATTR.get(operator)
                    if not semgrep_attr:
                        raise AttributeError(f'BQL filter condition contains an unknown operator: {operator}')
                    conf.append({semgrep_attr: definition_value})

        return conf