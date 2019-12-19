import logging
import os
from os import path

import hcl2


class Parser():
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
                            dict = hcl2.load(file)
                            tf_defenition = dict
                            tf_definitions[tf_file] = tf_defenition
                            # TODO move from here
                            # tf_defenitions = context_registry.enrich_context(tf_file,tf_defenitions)

                            for modules in dict.get("module", []):
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
