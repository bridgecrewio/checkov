from typing import Dict, Any, List

from hcl2 import START_LINE, END_LINE

from checkov.terraform.context_parsers.base_parser import BaseContextParser
import dpath


class LocalsContextParser(BaseContextParser):
    def __init__(self) -> None:
        definition_type = "locals"
        super().__init__(definition_type=definition_type)

    def _collect_local_values(self, local_block: Dict[str, Any]) -> None:
        for local_name, local_value in local_block.items():
            if local_name in {START_LINE, END_LINE}:
                continue

            local_value = local_value[0] if isinstance(local_value, list) and len(local_value) > 0 else local_value
            if type(local_value) in (int, float, bool, str, dict):
                dpath.new(self.context, ["assignments", local_name], local_value)

    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        return []

    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        for entity_block in definition_blocks:
            if START_LINE in entity_block.keys():
                self.context["start_line"] = entity_block[START_LINE]
            if END_LINE in entity_block.keys():
                self.context["end_line"] = entity_block[END_LINE]
            if "start_line" in self.context and "end_line" in self.context:
                self.context["code_lines"] = self.file_lines[self.context["start_line"] - 1: self.context["end_line"]]

            if isinstance(entity_block, dict):
                self._collect_local_values(entity_block)
        return self.context


parser = LocalsContextParser()
