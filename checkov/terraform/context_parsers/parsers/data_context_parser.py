from checkov.terraform.context_parsers.base_parser import BaseContextParser


class DataContextParser(BaseContextParser):
    def __init__(self):
        definition_type = 'data'
        super().__init__(definition_type=definition_type)

    def get_block_type(self):
        return self.definition_type


parser = DataContextParser()
