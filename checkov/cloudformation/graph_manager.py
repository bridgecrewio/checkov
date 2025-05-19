from __future__ import annotations

import json
import logging
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Any

from checkov.cloudformation.cfn_utils import get_folder_definitions
from checkov.cloudformation.context_parser import ContextParser
from checkov.cloudformation.graph_builder.graph_to_definitions import convert_graph_vertices_to_definitions
from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_manager import GraphManager

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraphConnector


class CloudformationGraphManager(GraphManager[CloudformationLocalGraph, "dict[str, dict[str, Any]]"]):
    def __init__(self, db_connector: LibraryGraphConnector, source: str = GraphSource.CLOUDFORMATION) -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: type[CloudformationLocalGraph] = CloudformationLocalGraph,
        render_variables: bool = True,
        parsing_errors: Optional[Dict[str, Exception]] = None,
        download_external_modules: Optional[bool] = False,
        excluded_paths: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Tuple[CloudformationLocalGraph, dict[str, dict[str, Any]]]:
        logging.info(f"[CloudformationGraphManager] Parsing files in source dir {source_dir}")
        parsing_errors = {} if parsing_errors is None else parsing_errors
        definitions, definitions_raw = get_folder_definitions(source_dir, excluded_paths, parsing_errors)  # type:ignore[arg-type]
        local_graph = self.build_graph_from_definitions(definitions, render_variables)
        rendered_definitions, _ = convert_graph_vertices_to_definitions(local_graph.vertices, source_dir)

        # TODO: replace with real graph rendering
        for cf_file in rendered_definitions.keys():
            file_definition = rendered_definitions.get(cf_file, None)
            file_definition_raw = definitions_raw.get(cf_file, None)
            if file_definition is not None and file_definition_raw is not None:
                cf_context_parser = ContextParser(cf_file, file_definition, file_definition_raw)
                logging.debug(
                    f"Template Dump for {cf_file}: {json.dumps(file_definition, indent=2, default=str)}"
                )
                cf_context_parser.evaluate_default_refs()
        return local_graph, rendered_definitions

    def build_graph_from_definitions(
        self, definitions: dict[str, dict[str, Any]], render_variables: bool = True
    ) -> CloudformationLocalGraph:
        local_graph = CloudformationLocalGraph(definitions, source=self.source)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
