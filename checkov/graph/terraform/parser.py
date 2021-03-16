import logging
import os
from copy import deepcopy
from checkov.terraform.parser import Parser
from checkov.graph.terraform.graph_builder.graph_components.module import Module
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR

from checkov.graph.terraform.graph_builder.utils import remove_module_dependency_in_path

external_modules_download_path = os.environ.get('EXTERNAL_MODULES_DIR', DEFAULT_EXTERNAL_MODULES_DIR)


class TerraformGraphParser(Parser):
    def __init__(self, module_class=Module):
        super().__init__()
        self.module_class = module_class

    def parse_hcl_module(self, source_dir, source):
        tf_definitions = {}
        parsing_errors = {}
        download_external_modules = os.environ.get('DOWNLOAD_EXTERNAL_MODULES', 'false').lower() == 'true'
        self.parse_directory(directory=source_dir, out_definitions=tf_definitions, out_evaluations_context={},
                             out_parsing_errors=parsing_errors,
                             download_external_modules=download_external_modules, evaluate_variables=False,
                             external_modules_download_path=external_modules_download_path)
        tf_definitions = TerraformGraphParser._hcl_boolean_types_to_boolean(tf_definitions)
        return self.parse_hcl_module_from_tf_definitions(tf_definitions, source_dir, source)

    def parse_hcl_module_from_tf_definitions(self, tf_definitions, source_dir, source):
        module = self.get_new_module(source_dir)
        module_dependency_map, tf_definitions = self.get_module_dependency_map(tf_definitions)
        copy_of_tf_definitions = deepcopy(tf_definitions)
        for file_path in copy_of_tf_definitions:
            blocks = copy_of_tf_definitions.get(file_path)
            for block_type in blocks:
                try:
                    module.add_blocks(block_type, blocks[block_type], file_path, source)
                except Exception as e:
                    logging.error(f'Failed to add block {blocks[block_type]}. Error:')
                    logging.error(e, exc_info=True)
        return module, module_dependency_map, tf_definitions

    @staticmethod
    def _hcl_boolean_types_to_boolean(conf: dict) -> dict:
        sorted_keys = sorted(filter(lambda x: x is not None, conf.keys()))
        # Create a new dict where the keys are sorted alphabetically
        sorted_conf = {key: conf[key] for key in sorted_keys}
        for attribute, values in sorted_conf.items():
            if attribute is 'alias':
                continue
            if isinstance(values, list):
                sorted_conf[attribute] = TerraformGraphParser._hcl_boolean_types_to_boolean_lst(values)
            elif isinstance(values, dict):
                sorted_conf[attribute] = TerraformGraphParser._hcl_boolean_types_to_boolean(conf[attribute])
            elif isinstance(values, str) and values in ('true', 'false'):
                sorted_conf[attribute] = True if values == 'true' else False
        return sorted_conf

    @staticmethod
    def _hcl_boolean_types_to_boolean_lst(values: list) -> list:
        for i in range(len(values)):
            val = values[i]
            if isinstance(val, dict):
                values[i] = TerraformGraphParser._hcl_boolean_types_to_boolean(val)
            elif isinstance(val, list):
                values[i] = TerraformGraphParser._hcl_boolean_types_to_boolean_lst(val)
            elif isinstance(val, str):
                if val == 'true':
                    values[i] = True
                elif val == 'false':
                    values[i] = False
        str_values_in_lst = [val for val in values if isinstance(val, str)]
        str_values_in_lst.sort()
        result_values = [val for val in values if not isinstance(val, str)]
        result_values.extend(str_values_in_lst)
        return result_values

    @staticmethod
    def get_module_dependency_map(tf_definitions):
        """
        :param tf_definitions, with paths in format 'dir/main.tf[module_dir/main.tf#0]'
        :return module_dependency_map: mapping between directories and the location of its module definition:
                {'dir': 'module_dir/main.tf'}
        :return tf_definitions: with paths in format 'dir/main.tf'
        """
        module_dependency_map = {}
        copy_of_tf_definitions = {}
        for file_path in tf_definitions.keys():
            path, module_dependency = remove_module_dependency_in_path(file_path)
            dir_name = os.path.dirname(path)
            if not module_dependency_map.get(dir_name):
                module_dependency_map[dir_name] = module_dependency
            copy_of_tf_definitions[path] = deepcopy(tf_definitions[file_path])
        return module_dependency_map, copy_of_tf_definitions

    def get_new_module(self, source_dir):
        return Module(source_dir)
