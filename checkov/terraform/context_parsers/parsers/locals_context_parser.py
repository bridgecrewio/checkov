from typing import Dict, Any, List

from checkov.terraform.context_parsers.base_parser import BaseContextParser
import dpath.util


class LocalsContextParser(BaseContextParser):
    def __init__(self) -> None:
        definition_type = "locals"
        super().__init__(definition_type=definition_type)

    def _collect_local_values(self, local_block: Dict[str, Any]) -> None:
        for local_name, local_value in local_block.items():
            local_value = local_value[0] if isinstance(local_value, list) and len(local_value) > 0 else local_value
            if type(local_value) in (int, float, bool, str, dict):
                dpath.new(self.context, ["assignments", local_name], local_value)

    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        return []

    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.context = super().enrich_definition_block(definition_blocks)
        for locals_block in definition_blocks:
            if isinstance(locals_block, dict):
                self._collect_local_values(locals_block)
        return self.context


parser = LocalsContextParser()
