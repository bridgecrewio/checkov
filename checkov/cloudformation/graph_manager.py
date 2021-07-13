import logging
from typing import List

from checkov.cloudformation.cfn_utils import get_folder_definitions
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.common.graph.graph_manager import GraphManager


class CloudformationGraphManager(GraphManager):
    def __init__(self, db_connector, source='CloudFormation'):
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(self, source_dir,
                                          render_variables=False,
                                          local_graph_class=CloudformationLocalGraph,
                                          parsing_errors=None,
                                          download_external_modules=False,
                                          excluded_paths: List[str] = None):
        logging.info('[CloudformationGraphManager] Parsing files in source dir {source_dir}')
        definitions, definitions_raw = get_folder_definitions(source_dir, excluded_paths)
        logging.info('[CloudformationGraphManager] Building graph from parsed definitions')

        local_graph = local_graph_class(definitions, source=self.source)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph, definitions

    def build_graph_from_definitions(self, definitions, render_variables=False):
        local_graph = CloudformationLocalGraph(definitions, source=self.source)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
