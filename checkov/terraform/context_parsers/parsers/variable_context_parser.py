from typing import Dict, Any, List

import dpath.util
from hcl2 import START_LINE, END_LINE

from checkov.terraform.context_parsers.base_parser import BaseContextParser


class VariableContextParser(BaseContextParser):
    def __init__(self) -> None:
        definition_type = "variable"
        super().__init__(definition_type=definition_type)

    def _collect_default_variables_values(self, variable_block: Dict[str, Dict[str, Any]]) -> None:
        for variable_name, values in variable_block.items():
            default_value = values.get("default")
            if (
                isinstance(default_value, list)
                and len(default_value) == 1
                and type(default_value[0]) in (int, float, bool, str)
            ):
                dpath.new(self.context, ["assignments", variable_name], default_value[0])

    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        entity_name = next(iter(entity_block.keys()))
        return [entity_name]

    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        for entity_block in definition_blocks:
            entity_name, entity_config = next(iter(entity_block.items()))
            self.context[entity_name] = {
                "start_line": entity_config[START_LINE],
                "end_line": entity_config[END_LINE],
                "code_lines": self.file_lines[entity_config[START_LINE] - 1: entity_config[END_LINE]],
            }

            if isinstance(entity_block, dict):
                self._collect_default_variables_values(entity_block)
        return self.context


parser = VariableContextParser()
