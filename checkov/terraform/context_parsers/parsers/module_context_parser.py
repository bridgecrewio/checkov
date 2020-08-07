from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ModuleContextParser(BaseContextParser):
    def __init__(self):
        definition_type = "module"
        super().__init__(definition_type=definition_type)

    def get_entity_context_path(self, entity_block):
        entity_name = next(iter(entity_block.keys()))
        return ["module", entity_name]


parser = ModuleContextParser()
