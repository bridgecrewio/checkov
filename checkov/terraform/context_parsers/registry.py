import logging
import dpath.util


class ParserRegistry:
    context_parsers = {}
    definitions_context = {}

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def register(self, parser):
        self.context_parsers[parser.definition_type] = parser

    def reset_definitions_context(self):
        self.definitions_context = {}

    def enrich_definitions_context(self, definitions, collect_skip_comments=True):
        supported_definitions = [parser_type for parser_type in self.context_parsers.keys()]
        (tf_file, definition_blocks_types) = definitions
        if definition_blocks_types:
            definition_blocks_types = {x: definition_blocks_types[x] for x in definition_blocks_types.keys()}
            for definition_type in definition_blocks_types.keys():
                if definition_type in supported_definitions:
                    dpath.new(self.definitions_context, [tf_file, definition_type], {})
                    context_parser = self.context_parsers[definition_type]
                    definition_blocks = definition_blocks_types[definition_type]
                    self.definitions_context[tf_file][definition_type] = context_parser.run(tf_file, definition_blocks, collect_skip_comments)

        return self.definitions_context


parser_registry = ParserRegistry()
