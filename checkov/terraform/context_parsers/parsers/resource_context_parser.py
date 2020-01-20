from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ResourceContextParser(BaseContextParser):
    def __init__(self):
        definition_type = 'resource'
        super().__init__(definition_type=definition_type)

    def get_block_type(self):
        return self.definition_type


parser = ResourceContextParser()
