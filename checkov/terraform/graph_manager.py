import logging
from typing import List, Optional, Dict, Type, Tuple, Any

from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.graph.graph_manager import GraphManager
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.parser import Parser


class TerraformGraphManager(GraphManager):
    def __init__(self, db_connector, source=""):
        super().__init__(db_connector=db_connector, parser=Parser(), source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        render_variables: bool = True,
        local_graph_class: Type[LocalGraph] = TerraformLocalGraph,
        parsing_errors: Optional[Dict[str, Exception]] = None,
        download_external_modules: bool = False,
        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
        excluded_paths: Optional[List[str]] = None,
        vars_files: Optional[List[str]] = None,
    ) -> Tuple[LocalGraph, Dict[str, Dict[str, Any]]]:
        logging.info("Parsing HCL files in source dir")
        module, tf_definitions = self.parser.parse_hcl_module(
            source_dir=source_dir,
            source=self.source,
            download_external_modules=download_external_modules,
            external_modules_download_path=external_modules_download_path,
            parsing_errors=parsing_errors,
            excluded_paths=excluded_paths,
            vars_files=vars_files,
        )

        logging.info("Building graph from parsed module")
        local_graph = local_graph_class(module)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph, tf_definitions

    def build_graph_from_definitions(
        self, definitions: Dict[str, Dict[str, Any]], render_variables: bool = True
    ) -> TerraformLocalGraph:
        module, _ = self.parser.parse_hcl_module_from_tf_definitions(definitions, "", self.source)
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
