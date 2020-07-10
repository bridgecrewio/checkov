from checkov.terraform.context_parsers.base_parser import BaseContextParser
import os
import dpath.util


class VariableContextParser(BaseContextParser):
    def __init__(self):
        definition_type = "variable"
        super().__init__(definition_type=definition_type)

    def _collect_default_variables_values(self, variable_block):
        (variable_folder, _) = os.path.split(self.tf_file)
        if isinstance(variable_block,dict):
            for variable_name, values in variable_block.items():
                if 'default' in values.keys():
                    for key, value in values.items():
                        if isinstance(value, list) and len(value) == 1:
                            value = values['default'][0]
                            if type(value) in (int, float, bool, str):
                                dpath.new(self.context, ['assignments', variable_name], value)

    def get_entity_context_path(self, entity_block):
        return []

    def enrich_definition_block(self, definition_blocks):
        self.context = super().enrich_definition_block(definition_blocks)
        for i, variable_block in enumerate(definition_blocks):
            self._collect_default_variables_values(variable_block)
        return self.context


parser = VariableContextParser()
