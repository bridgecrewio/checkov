import re
from typing import Any, Dict, Tuple


class K8sValidator:
    name_disallowed_chars = re.compile("[#{}]+")  # noqa: CCE003  # a static attribute

    @staticmethod
    def is_valid_template(template: Any) -> Tuple[bool, str]:
        is_valid = isinstance(template, dict)
        if not is_valid:
            return is_valid, f'template is not a dict, but {type(template)}'

        is_valid, reason = K8sValidator._has_required_fields(template)
        if not is_valid:
            return is_valid, reason

        is_valid, reason = K8sValidator._is_section_valid(template)
        if not is_valid:
            return is_valid, reason

        return True, ''

    @staticmethod
    def _has_required_fields(template: Dict[str, Any]) -> Tuple[bool, str]:
        for key in ['apiVersion', 'kind']:
            if key not in template.keys():
                return False, f'the key {key} does not exist in template structure'
        return True, ''

    @staticmethod
    def _is_section_valid(template: Dict[str, Any]) -> Tuple[bool, str]:
        for segment in template.keys():
            if isinstance(template[segment], dict):
                is_section_valid, reason = K8sValidator._is_section_valid(template[segment])
                if not is_section_valid:
                    return is_section_valid, reason
            elif isinstance(template[segment], list):
                for entry in template[segment]:
                    if isinstance(entry, dict):
                        is_section_valid, reason = K8sValidator._is_section_valid(entry)
                        if not is_section_valid:
                            return is_section_valid, reason
            elif segment == 'name':
                is_section_valid, reason = K8sValidator._is_name_valid(template[segment])
                if not is_section_valid:
                    return is_section_valid, reason
        return True, ''

    @staticmethod
    def _is_name_valid(name: Any) -> Tuple[bool, str]:
        if not isinstance(name, str) or len(name) > 253:
            return False, f'name {name} is invalid'
        if K8sValidator.name_disallowed_chars.search(name):
            return False, f'name {name} is invalid'
        return True, ''
