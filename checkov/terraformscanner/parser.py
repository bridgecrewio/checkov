import os
import hcl2
from checkov.terraformscanner.context_parsers.parser_registry import parser_registry
import logging

class Parser():
    logger = logging.getLogger(__name__)

    def hcl2(self, directory, tf_defenitions={}):
        modules_scan = []
        for file in os.listdir(directory):
            if file.endswith(".tf"):
                tf_file = os.path.join(directory, file)
                if tf_file not in tf_defenitions.keys():
                    try:
                        with(open(tf_file, 'r')) as file:
                            file.seek(0)
                            dict = hcl2.load(file)
                            tf_defenition = dict
                            tf_defenitions[tf_file] = tf_defenition
                            # TODO move from here
                            # tf_defenitions = context_registry.enrich_context(tf_file,tf_defenitions)

                            for modules in dict.get("module", []):
                                for module in modules.values():
                                    relative_path = module['source'][0]
                                    abs_path = os.path.join(directory, relative_path)
                                    modules_scan.append(abs_path)
                    except Exception as e:
                        self.logger.error('failed while parsing file %s' % tf_file,  exc_info=e)
        for m in modules_scan:
            self.hcl2(directory=m, tf_defenitions=tf_defenitions)
