import logging
from typing import List

from checkov.common.graph.graph_manager import GraphManager
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.parser import Parser


class TerraformGraphManager(GraphManager):
    def __init__(self, db_connector, source=''):
        super().__init__(db_connector=db_connector, parser=Parser(), source=source)

    def build_graph_from_source_directory(self, source_dir, render_variables=True, local_graph_class=TerraformLocalGraph,
                                          parsing_errors=None, download_external_modules=False, excluded_paths: List[str]=None):
        logging.info('Parsing HCL files in source dir')
        module, module_dependency_map, tf_definitions = \
            self.parser.parse_hcl_module(source_dir, self.source, download_external_modules, parsing_errors, excluded_paths=excluded_paths)

        logging.info('Building graph from parsed module')
        local_graph = local_graph_class(module, module_dependency_map)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph, tf_definitions

    def build_graph_from_definitions(self, definitions, render_variables=True):
        module, module_dependency_map, _ = \
            self.parser.parse_hcl_module_from_tf_definitions(definitions, '', self.source)
        local_graph = TerraformLocalGraph(module, module_dependency_map)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
