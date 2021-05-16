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


parser = DataContextParser()
