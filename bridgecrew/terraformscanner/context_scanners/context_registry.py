import logging
import re

class ContextRegistry():

    context_scanners = {}

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def register(self,scanner):
         self.context_scanners[scanner] = scanner

    def enrich_context(self,tf_file,tf_definitions):
        with(open(tf_file, 'r')) as file:
            file.seek(0)
            file_lines = [(ind + 1, re.sub('\s+', ' ', line).strip()) for (ind, line) in
                      list(enumerate(file.readlines()))]
            file_lines = [(ind, line) for (ind, line) in file_lines if line]
            for definition_block in tf_definitions.keys():
                pass

            return tf_definitions


context_registry = ContextRegistry()