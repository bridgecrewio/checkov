from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ResourceContextParser(BaseContextParser):
    def __init__(self):
        definition_type = "resource"
        super().__init__(definition_type=definition_type)

    def _is_block_signature(self, line_tokens, entity_context_path):
        block_type = self.get_block_type()
        entity_type, entity_name = entity_context_path
        return all(x in line_tokens for x in [block_type, entity_type, entity_name])

    def get_entity_context_path(self, entity_block):
        entity_type = next(iter(entity_block.keys()))
        entity_name = next(iter(entity_block[entity_type]))
        return [entity_type, entity_name]


parser = ResourceContextParser()
