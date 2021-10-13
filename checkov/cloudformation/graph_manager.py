import json
import logging
from typing import List, Dict, Type, Optional, Tuple

from checkov.cloudformation.cfn_utils import get_folder_definitions
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.common.parsers.node import DictNode
from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_manager import GraphManager


class CloudformationGraphManager(GraphManager):
    def __init__(self, db_connector: DBConnector, source: str = "CloudFormation") -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        render_variables: bool = True,
        local_graph_class: Type[CloudformationLocalGraph] = CloudformationLocalGraph,
        parsing_errors: Optional[Dict[str, Exception]] = None,
        download_external_modules: bool = False,
        excluded_paths: Optional[List[str]] = None,
    ) -> Tuple[CloudformationLocalGraph, Dict[str, DictNode]]:
        logging.info("[CloudformationGraphManager] Parsing files in source dir {source_dir}")
        parsing_errors = {}
        definitions, definitions_raw = get_folder_definitions(source_dir, excluded_paths, parsing_errors)
        local_graph = self.build_graph_from_definitions(definitions, render_variables)
        rendered_definitions, _ = convert_graph_vertices_to_definitions(local_graph.vertices, source_dir)

        # TODO: replace with real graph rendering
        for cf_file in rendered_definitions.keys():
            file_definition = rendered_definitions.get(cf_file, None)
            file_definition_raw = definitions_raw.get(cf_file, None)
            if file_definition is not None and file_definition_raw is not None:
                cf_context_parser = ContextParser(cf_file, file_definition, file_definition_raw)
                logging.debug(
                    "Template Dump for {}: {}".format(cf_file, json.dumps(file_definition, indent=2, default=str))
                )
                cf_context_parser.evaluate_default_refs()
        return local_graph, rendered_definitions

    def build_graph_from_definitions(
        self, definitions: Dict[str, DictNode], render_variables: bool = True
    ) -> CloudformationLocalGraph:
        local_graph = CloudformationLocalGraph(definitions, source=self.source)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
