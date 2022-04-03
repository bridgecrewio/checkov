from typing import Dict, Any, List

from checkov.terraform.context_parsers.base_parser import BaseContextParser


class DataContextParser(BaseContextParser):
    def __init__(self) -> None:
        definition_type = "data"
        super().__init__(definition_type=definition_type)

    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        entity_type, entity_value = next(iter(entity_block.items()))
        entity_name = next(iter(entity_value))
        return [entity_type, entity_name]

    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        for i, entity_block in enumerate(definition_blocks):
            entity_type, entity_value = next(iter(entity_block.items()))
            entity_name, entity_config = next(iter(entity_value.items()))

            self.context[entity_type][entity_name] = {
                "start_line": entity_config["__start_line__"],
                "end_line": entity_config["__end_line__"],
                "code_lines": self.file_lines[entity_config["__start_line__"] - 1: entity_config["__end_line__"]],
            }


        return self.context


parser = DataContextParser()
