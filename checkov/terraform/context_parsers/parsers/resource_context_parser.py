from typing import Dict, Any, List

from hcl2 import END_LINE, START_LINE

from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ResourceContextParser(BaseContextParser):
    def __init__(self) -> None:
        definition_type = "resource"
        super().__init__(definition_type=definition_type)

    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        entity_type = next(iter(entity_block.keys()))
        entity_name = next(iter(entity_block[entity_type]))
        return [entity_type, entity_name]

    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        for entity_block in definition_blocks:
            entity_type, entity_value = next(iter(entity_block.items()))
            entity_name, entity_config = next(iter(entity_value.items()))

            self.context[entity_type][entity_name] = {
                "start_line": entity_config[START_LINE],
                "end_line": entity_config[END_LINE],
                "code_lines": self.file_lines[entity_config[START_LINE] - 1: entity_config[END_LINE]],
            }


        return self.context


parser = ResourceContextParser()
