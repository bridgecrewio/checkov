from checkov.terraform.context_parsers.base_parser import BaseContextParser


class DataContextParser(BaseContextParser):
    def __init__(self):
        definition_type = "data"
        super().__init__(definition_type=definition_type)

    def get_entity_context_path(self, entity_block):
        entity_type = next(iter(entity_block.keys()))
        entity_name = next(iter(entity_block[entity_type]))
        return [entity_type, entity_name]


parser = DataContextParser()
