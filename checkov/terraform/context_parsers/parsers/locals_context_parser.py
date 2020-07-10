from checkov.terraform.context_parsers.base_parser import BaseContextParser
import dpath.util


class LocalsContextParser(BaseContextParser):
    def __init__(self):
        definition_type = "locals"
        super().__init__(definition_type=definition_type)

    def _collect_local_values(self, local_block):
        if isinstance(local_block,dict):
            for local_name, local_value in local_block.items():
                local_value = local_value[0]
                if type(local_value) in (int, float, bool, str):
                    dpath.new(self.context, ['assignments', local_name], local_value)

    def get_block_type(self):
        return self.definition_type

    def get_entity_context_path(self, entity_block):
        return []

    def enrich_definition_block(self, definition_blocks):
        self.context = super().enrich_definition_block(definition_blocks)
        for i, locals_block in enumerate(definition_blocks):
            self._collect_local_values(locals_block)
        return self.context


parser = LocalsContextParser()
