import logging
import os
from os import path

import hcl2


class Parser:
    logger = logging.getLogger(__name__)

    def hcl2(self, directory, tf_definitions={}, parsing_errors={}):
        modules_scan = []

        for file in os.listdir(directory):
            if file.endswith(".tf"):
                tf_file = os.path.join(directory, file)
                if tf_file not in tf_definitions.keys():
                    try:
                        with(open(tf_file, 'r')) as file:
                            file.seek(0)
                            tf_definition = hcl2.load(file)
                            for resource_type in tf_definition.get('resource', []):
                                for resource in resource_type.values():
                                    for named_resource in resource.values():
                                        for dynamic_block in named_resource.get('dynamic', []):
                                            for dynamic_field_name, dynamic_field_value in dynamic_block.items():
                                                named_resource[dynamic_field_name] = dynamic_field_value['for_each']
                            tf_definitions[tf_file] = tf_definition
                            # TODO move from here
                            # tf_defenitions = context_registry.enrich_context(tf_file,tf_defenitions)

                            for modules in tf_definition.get("module", []):
                                for module in modules.values():
                                    relative_path = module['source'][0]
                                    abs_path = os.path.join(directory, relative_path)
                                    modules_scan.append(abs_path)
                    except Exception as e:
                        self.logger.debug('failed while parsing file %s' % tf_file, exc_info=e)
                        parsing_errors[tf_file] = e
        for m in modules_scan:
            if path.exists(m):
                self.hcl2(directory=m, tf_definitions=tf_definitions)

    def parse_file(self, file, tf_definitions={}, parsing_errors={}):
        if file.endswith(".tf"):
            try:
                with(open(file, 'r')) as tf_file:
                    tf_file.seek(0)
                    dict = hcl2.load(tf_file)
                    tf_defenition = dict
                    tf_definitions[file] = tf_defenition
            except Exception as e:
                self.logger.debug('failed while parsing file %s' % file, exc_info=e)
                parsing_errors[file] = e
