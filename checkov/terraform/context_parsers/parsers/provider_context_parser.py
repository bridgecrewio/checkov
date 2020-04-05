from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ProviderContextParser(BaseContextParser):
    def __init__(self):
        definition_type = "provider"
        super().__init__(definition_type=definition_type)

    def get_entity_context_path(self, entity_block):
        entity_type = next(iter(entity_block))
        return [entity_type]


parser = ProviderContextParser()
