from typing import Dict, Any, Tuple

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.util.consts import START_LINE, END_LINE


class Registry(BaseCheckRegistry):
    def extract_entity_details(self, entity: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        terraform_configuration = dict(entity.items())

        if START_LINE not in terraform_configuration or END_LINE not in terraform_configuration:
            start_lines = []
            end_lines = []

            def find_line_numbers(d):
                for k, v in d.items():
                    if k == START_LINE:
                        start_lines.append(v)
                    elif k == END_LINE:
                        end_lines.append(v)
                    elif isinstance(v, dict):
                        find_line_numbers(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                find_line_numbers(item)

            find_line_numbers(terraform_configuration)

            if start_lines and end_lines:
                terraform_configuration[START_LINE] = min(start_lines)
                terraform_configuration[END_LINE] = max(end_lines)
            else:
                terraform_configuration[START_LINE] = 1
                terraform_configuration[END_LINE] = 1

        return "terraform", "terraform", terraform_configuration
