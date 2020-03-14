from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ProviderContextParser(BaseContextParser):
    def __init__(self):
        definition_type = 'provider'
        super().__init__(definition_type=definition_type)

    def get_block_type(self):
        return self.definition_type

    def get_entity_name_and_type(self, entity_block):
        entity_type = self.definition_type
        entity_name = next(iter(entity_block))
        return entity_name, entity_type


parser = ProviderContextParser()
