from typing import Dict, Any, Tuple

from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def extract_entity_details(self, entity: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        terraform_configuration = dict(entity.items())

        if '__startline__' not in terraform_configuration or '__endline__' not in terraform_configuration:
            start_lines = []
            end_lines = []

            def find_line_numbers(d):
                for k, v in d.items():
                    if k == '__startline__':
                        start_lines.append(v)
                    elif k == '__endline__':
                        end_lines.append(v)
                    elif isinstance(v, dict):
                        find_line_numbers(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                find_line_numbers(item)

            find_line_numbers(terraform_configuration)

            if start_lines and end_lines:
                terraform_configuration['__startline__'] = min(start_lines)
                terraform_configuration['__endline__'] = max(end_lines)
            else:
                terraform_configuration['__startline__'] = 1
                terraform_configuration['__endline__'] = 1

        return "terraform", "terraform", terraform_configuration
