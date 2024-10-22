from __future__ import annotations

import logging
from typing import Dict, TYPE_CHECKING, Tuple, List, Any

import dpath

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.terraform.modules.module_objects import TFDefinitionKey

if TYPE_CHECKING:
    from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ParserRegistry:
    context_parsers: Dict[str, "BaseContextParser"] = {}  # noqa: CCE003
    definitions_context: Dict[TFDefinitionKey, Dict[str, Dict[str, Any]]] = {}  # noqa: CCE003

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        add_resource_code_filter_to_logger(self.logger)

    def register(self, parser: "BaseContextParser") -> None:
        self.context_parsers[parser.definition_type] = parser

    def reset_definitions_context(self) -> None:
        self.definitions_context = {}

    def enrich_definitions_context(
        self, definitions: Tuple[TFDefinitionKey, Dict[str, List[Dict[str, Any]]]], collect_skip_comments: bool = True
    ) -> Dict[TFDefinitionKey, Dict[str, Dict[str, Any]]]:
        supported_definitions = [parser_type for parser_type in self.context_parsers.keys()]
        (tf_definition_key, definition_blocks_types) = definitions

        if definition_blocks_types:
            definition_blocks_types = {x: definition_blocks_types[x] for x in definition_blocks_types.keys()}
            for definition_type in definition_blocks_types.keys():
                if definition_type in supported_definitions:
                    dpath.new(self.definitions_context, [tf_definition_key, definition_type], {})
                    context_parser = self.context_parsers[definition_type]
                    definition_blocks = definition_blocks_types[definition_type]
                    self.definitions_context[tf_definition_key][definition_type] = \
                        context_parser.run(tf_definition_key, definition_blocks, collect_skip_comments)
        return self.definitions_context


parser_registry = ParserRegistry()
