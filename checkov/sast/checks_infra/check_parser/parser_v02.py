from __future__ import annotations

from typing import Dict, Any, List

from checkov.sast.consts import SemgrepAttribute, BqlV2ConditionType, BQLV2_KEY_TO_SEMGREP_ATTR, \
    BQLV2_METAVAR_KEY_TO_SEMGREP_ATTR
from checkov.sast.checks_infra.check_parser.base_parser import BaseSastCheckParser


class SastCheckParserV02(BaseSastCheckParser):
    def _parse_definition(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(definition, dict):
            raise TypeError(f'bad definition type, got {type(definition)} instead of dict')

        conf: Dict[str, Any] = {}
        single_conditions = []

        for k, v in definition.items():
            if k == BqlV2ConditionType.OR:
                conf.setdefault(str(SemgrepAttribute.PATTERN_EITHER), [])
                for condition in v:
                    conf[str(SemgrepAttribute.PATTERN_EITHER)].append(self._parse_definition(condition))

            elif k == BqlV2ConditionType.AND:
                conf.setdefault(str(SemgrepAttribute.PATTERNS), [])
                for condition in v:
                    conf[str(BqlV2ConditionType.PATTERNS)].append(self._parse_definition(condition))

            elif k == BqlV2ConditionType.PATTERNS:
                if isinstance(v, dict):
                    conf.update(self._parse_definition(v))
                else:
                    conf.setdefault(str(SemgrepAttribute.PATTERNS), [])
                    conf[str(BqlV2ConditionType.PATTERNS)].extend(self._parse_definition(v))

            elif k == BqlV2ConditionType.CONDITIONS:
                conf.setdefault(str(SemgrepAttribute.PATTERNS), [])
                for condition in v:
                    if str(BqlV2ConditionType.METAVARIABLE) in condition:
                        conf[str(BqlV2ConditionType.PATTERNS)].append(self._parse_metavariable_condition(condition))
                    else:
                        for ck, cv in condition.items():
                            conf[str(BqlV2ConditionType.PATTERNS)].append(self._parse_single_condition(ck, cv))

            else:
                single_conditions.append(self._parse_single_condition(k, v))

        if single_conditions:
            if len(single_conditions) == 1 and str(SemgrepAttribute.PATTERNS) not in conf:
                conf.update(single_conditions[0])
            else:
                conf.setdefault(str(SemgrepAttribute.PATTERNS), [])
                conf[str(BqlV2ConditionType.PATTERNS)].extend(single_conditions)

        return conf

    def _parse_single_condition(self, key: str, value: str) -> Dict[str, str]:
        attribute = BQLV2_KEY_TO_SEMGREP_ATTR.get(key, '')
        if not attribute:
            raise AttributeError(f'unsupported definition field: {key}')

        return {attribute: value.replace('<ANY>', '...')}

    def _parse_metavariable_condition(self, cond: Dict[str, str]) -> Dict[str, Any]:
        metavar_conf = {}
        attribute = ''
        for k, v in cond.items():
            metavar_conf[k] = v
            attribute = BQLV2_METAVAR_KEY_TO_SEMGREP_ATTR.get(k, '')
        if not attribute:
            raise AttributeError(f'unsupported metavariable condition: {cond}')

        return {attribute: metavar_conf}

    def _parse_taint_field(self, key: str, value: List[str | Dict[str, Any]] | str) -> List[Dict[str, Any]]:
        parsed_list = []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    parsed_list.append(self._parse_single_condition(key[:-1], item))
                elif isinstance(item, dict):
                    parsed_list.append(self._parse_definition(item))

        else:
            parsed_list.append(self._parse_single_condition(key, value))

        return parsed_list

    def _parse_taint_mode_definition(self, definition: Dict[str, Any]) -> Dict[str, Any]:
        conf: Dict[str, Any] = {
            str(SemgrepAttribute.PATTERN_SOURCES): [],
            str(SemgrepAttribute.PATTERN_SINKS): []
        }
        for k, v in definition.items():
            if k in [BqlV2ConditionType.SOURCE, BqlV2ConditionType.SOURCES]:
                conf[SemgrepAttribute.PATTERN_SOURCES].extend(self._parse_taint_field(k, v))

            elif k in [BqlV2ConditionType.SINK, BqlV2ConditionType.SINKS]:
                conf[SemgrepAttribute.PATTERN_SINKS].extend(self._parse_taint_field(k, v))

            elif k in [BqlV2ConditionType.SANITIZER, BqlV2ConditionType.SANITIZERS]:
                sanitizers_key = str(SemgrepAttribute.PATTERN_SANITIZERS)
                conf.setdefault(sanitizers_key, [])
                conf[sanitizers_key].extend(self._parse_taint_field(k, v))

            elif k in [BqlV2ConditionType.PROPAGATOR, BqlV2ConditionType.PROPAGATORS]:
                propagators_key = str(SemgrepAttribute.PATTERN_PROPAGATORS)
                conf.setdefault(propagators_key, [])
                conf[SemgrepAttribute.PATTERN_PROPAGATORS].extend(self._parse_taint_field(k, v))

            else:
                raise AttributeError(f'unsupported definition field: {k}')

        return conf
