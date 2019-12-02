import logging
import re


class ParserRegistry():
    context_parsers = {}

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def register(self, parser):
        self.context_parsers[parser] = parser

    def enrich_context(self, tf_file, tf_definitions):
        with(open(tf_file, 'r')) as file:
            file.seek(0)
            file_lines = [(ind + 1, re.sub('\s+', ' ', line).strip()) for (ind, line) in
                          list(enumerate(file.readlines()))]
            file_lines = [(ind, line) for (ind, line) in file_lines if line]
            for definition_block in tf_definitions.keys():
                pass

            return tf_definitions


parser_registry = ParserRegistry()