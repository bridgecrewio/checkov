import logging
from typing import Dict, Any, List

import hcl2
from hcl2 import START_LINE, END_LINE

from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ProviderContextParser(BaseContextParser):
    def __init__(self) -> None:
        definition_type = "provider"
        super().__init__(definition_type=definition_type)

    def get_entity_context_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        entity_type, entity_value = next(iter(entity_block.items()))
        return [entity_type, entity_value.get("alias", ["default"])[0]]

    def get_entity_definition_path(self, entity_block: Dict[str, Dict[str, Any]]) -> List[str]:
        entity_type, _ = next(iter(entity_block.items()))
        return [entity_type]

    def enrich_definition_block(self, definition_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        for entity_block in definition_blocks:
            entity_type, entity_config = next(iter(entity_block.items()))
            entity_name = entity_config.get("alias", ["default"])[0]
            self.context[entity_type][entity_name] = {
                "start_line": entity_config[START_LINE],
                "end_line": entity_config[END_LINE],
                "code_lines": self.file_lines[entity_config[START_LINE] - 1: entity_config[END_LINE]],
            }

        return self.context

    def _is_block_signature(self, line_num: int, line_tokens: List[str], entity_context_path: List[str]) -> bool:
        # Ignore the alias as it is not part of the signature
        is_provider = super()._is_block_signature(line_num, line_tokens, entity_context_path[0:-1])
        if not is_provider or "=" in line_tokens or line_tokens[0] != "provider":
            if not all(bracket in line_tokens for bracket in ("{", "}")):
                # The line provider = alias is not a provider block although it has the correct words
                # Also skips comments that include words like provider and aws
                return False

        end_line = self._compute_definition_end_line(line_num)
        provider_type = entity_context_path[0]
        try:
            provider_obj = hcl2.loads(
                "\n".join(
                    map(lambda obj: obj[1], self.file_lines[line_num - 1 : end_line if end_line > line_num else line_num])
                )
            )["provider"][0]
        except Exception as e:
            logging.info(f'got exception while loading file {self.tf_file}\n {e}')
            return False
        alias = provider_obj[provider_type].get("alias", ["default"])
        return super()._is_block_signature(line_num, line_tokens + alias, entity_context_path)


parser = ProviderContextParser()
