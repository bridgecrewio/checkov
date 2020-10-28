import logging
import os
from os import path

import hcl2
from checkov.common.runners.base_runner import filter_ignored_directories


class Parser:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._parsed_directories = set()

    def _mark_parsed(self, directory):
        self._parsed_directories.add(directory)

    def _is_parsed(self, directory):
        return directory in self._parsed_directories

    @staticmethod
    def clean_bad_definitions(tf_definition_list):
        return {
            block_type: list(filter(lambda definition_list: len(definition_list.keys()) == 1, tf_definition_list[block_type]))
            for block_type in tf_definition_list.keys()
        }

    @staticmethod
    def clean_bad_definitions(tf_definition_list):
        return {
            block_type: list(filter(lambda definition_list: block_type == 'locals' or len(definition_list.keys()) == 1, tf_definition_list[block_type]))
            for block_type in tf_definition_list.keys()
        }

    @staticmethod
    def _parse_tf_definitions(tf_file):
        with(open(tf_file, 'r')) as file:
            file.seek(0)
            raw_tf_definition = hcl2.load(file)
            tf_definition = Parser.clean_bad_definitions(raw_tf_definition)
            for resource_type in tf_definition.get('resource', []):
                for resource in resource_type.values():
                    for named_resource in resource.values():
                        for dynamic_block in named_resource.get('dynamic', []):
                            for dynamic_field_name, dynamic_field_value in dynamic_block.items():
                                named_resource[dynamic_field_name] = dynamic_field_value['for_each']
        return tf_definition

    def hcl2(self, directory, tf_definitions={}, parsing_errors={}):
        modules_scan = set()
        for root, d_names, f_names in os.walk(directory):
            filter_ignored_directories(d_names)
            self._mark_parsed(os.path.abspath(root))
            for file in f_names:
                if file.endswith(".tf"):
                    tf_file = os.path.join(root, file)
                    if tf_file not in tf_definitions.keys():
                        try:
                            tf_definition = self._parse_tf_definitions(tf_file)
                            if tf_definition:
                                tf_definitions[tf_file] = tf_definition
                            for modules in tf_definition.get("module", []):
                                for module in modules.values():
                                    relative_path = module['source'][0]
                                    abs_path = os.path.abspath(os.path.join(root, relative_path))
                                    if not self._is_parsed(abs_path):
                                        modules_scan.add(abs_path)
                        except Exception as e:
                            self.logger.debug(f'failed while parsing file {tf_file}', exc_info=e)
                            parsing_errors[tf_file] = e
        for m in modules_scan:
            if path.exists(m):
                self.hcl2(directory=m, tf_definitions=tf_definitions)

    def parse_file(self, file, parsing_errors={}):
        if file.endswith(".tf"):
            try:
                return self._parse_tf_definitions(file)
            except Exception as e:
                self.logger.warning(f'failed while parsing file {file}', exc_info=e)
                parsing_errors[file] = e
