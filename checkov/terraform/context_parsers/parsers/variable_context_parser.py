from checkov.terraform.context_parsers.base_parser import BaseContextParser
import os
import dpath.util


class VariableContextParser(BaseContextParser):
    def __init__(self):
        definition_type = 'variable'
        super().__init__(definition_type=definition_type)

    def get_block_type(self):
        return self.definition_type

    def _collect_default_variables_values(self, variable_block):
        (variable_folder, _) = os.path.split(self.tf_file)
        for variable_name, values in variable_block.items():
            if 'default' in values.keys():
                for key, value in values.items():
                    if isinstance(value, list) and len(value) == 1:
                        value = values['default'][0]
                        if type(value) in (int, float, bool, str):
                            dpath.new(self.context, "//".join(['assignments', variable_name]), value,
                                      separator='//')

    def enrich_definition_block(self, block):
        # self.context = super().enrich_definition_block(block) # TODO, the base class does not generalize to a variable block
        self.context = {}
        for i, variable_block in enumerate(block):
            self._collect_default_variables_values(variable_block)
        return self.context


parser = VariableContextParser()
