import re
from typing import Any


class K8sValidator:
    name_disallowed_chars = re.compile("[#{}]+")  # noqa: CCE003  # a static attribute

    @staticmethod
    def is_valid_template(template: Any) -> bool:
        return isinstance(template, dict) and K8sValidator._has_required_fields(template) and K8sValidator._is_section_valid(template)

    @staticmethod
    def _has_required_fields(template: dict[str, Any]) -> bool:
        return bool({'apiVersion', 'kind', 'metadata', 'spec'} - template.keys() == set())

    @staticmethod
    def _is_section_valid(template: dict[str, Any]) -> bool:
        for segment in template.keys():
            if isinstance(template[segment], dict):
                if not K8sValidator._is_section_valid(template[segment]):
                    return False
            elif isinstance(template[segment], list):
                for entry in template[segment]:
                    if not K8sValidator._is_section_valid(entry):
                        return False
            elif segment == 'name':
                if not K8sValidator._is_name_valid(template[segment]):
                    return False
        return True

    @staticmethod
    def _is_name_valid(name: Any) -> bool:
        if not isinstance(name, str) or len(name) > 253:
            return False
        if K8sValidator.name_disallowed_chars.search(name):
            return False
        return True
