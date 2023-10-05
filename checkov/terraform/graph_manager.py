from __future__ import annotations

import logging
from typing import Type, Any, TYPE_CHECKING, overload

from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

from checkov.common.graph.graph_manager import GraphManager
from checkov.terraform.tf_parser import TFParser

if TYPE_CHECKING:
    from checkov.terraform.modules.module_objects import TFDefinitionKey
    from checkov.common.typing import LibraryGraphConnector


class TerraformGraphManager(GraphManager[TerraformLocalGraph, "dict[TFDefinitionKey, dict[str, Any]]"]):
    def __init__(self, db_connector: LibraryGraphConnector, source: str = "") -> None:
        self.parser: TFParser  # just to make sure it won't be None

        parser = TFParser()
        super().__init__(db_connector=db_connector, parser=parser, source=source)

    def build_multi_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: Type[TerraformLocalGraph] = TerraformLocalGraph,
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
        vars_files: list[str] | None = None,
        create_graph: bool = True,
    ) -> list[tuple[TerraformLocalGraph | None, list[dict[TFDefinitionKey, dict[str, Any]]], str]]:
        logging.info("Parsing HCL files in source dir to multi graph")
        modules_with_definitions = self.parser.parse_multi_graph_hcl_module(
            source_dir=source_dir,
            source=self.source,
            download_external_modules=download_external_modules,
            external_modules_download_path=external_modules_download_path,
            parsing_errors=parsing_errors,
            excluded_paths=excluded_paths,
            vars_files=vars_files,
            create_graph=create_graph,
        )

        graphs: list[tuple[TerraformLocalGraph | None, list[dict[TFDefinitionKey, dict[str, Any]]], str]] = []
        for module, tf_definitions in modules_with_definitions:
            if create_graph and module:
                logging.info("Building graph from parsed module")
                local_graph = local_graph_class(module)
                local_graph.build_graph(render_variables=render_variables)
                subgraph_abs_path = module.source_dir
                subgraph_path = subgraph_abs_path[subgraph_abs_path.rindex(source_dir) + len(source_dir) + 1:]
                graphs.append((local_graph, tf_definitions, subgraph_path))

        return graphs

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: Type[TerraformLocalGraph] = TerraformLocalGraph,
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
        vars_files: list[str] | None = None,
        create_graph: bool = True,
    ) -> tuple[TerraformLocalGraph | None, dict[TFDefinitionKey, dict[str, Any]]]:
        logging.info("Parsing HCL files in source dir to graph")
        module, tf_definitions = self.parser.parse_hcl_module(
            source_dir=source_dir,
            source=self.source,
            download_external_modules=download_external_modules,
            external_modules_download_path=external_modules_download_path,
            parsing_errors=parsing_errors,
            excluded_paths=excluded_paths,
            vars_files=vars_files,
            create_graph=create_graph,
        )

        local_graph = None
        if create_graph and module:
            logging.info("Building graph from parsed module")
            local_graph = local_graph_class(module)
            local_graph.build_graph(render_variables=render_variables)

        return local_graph, tf_definitions

    @overload
    def build_graph_from_definitions(
        self, definitions: dict[str, dict[str, Any]], render_variables: bool = True,
    ) -> TerraformLocalGraph:
        ...

    @overload
    def build_graph_from_definitions(
        self, definitions: dict[TFDefinitionKey, dict[str, Any]], render_variables: bool = True,
    ) -> TerraformLocalGraph:
        ...

    def build_graph_from_definitions(
        self,
        definitions: dict[str, dict[str, Any]] | dict[TFDefinitionKey, dict[str, Any]],
        render_variables: bool = True,
    ) -> TerraformLocalGraph:
        module, _ = self.parser.parse_hcl_module_from_tf_definitions(definitions, "", self.source)
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph

    def build_multi_graph_from_definitions(self, definitions: dict[TFDefinitionKey, dict[str, Any]],
                                           render_variables: bool = True) -> list[tuple[str, TerraformLocalGraph]]:
        module, tf_definitions = self.parser.parse_hcl_module_from_tf_definitions(definitions, "", self.source)
        dirs_to_definitions = self.parser.create_definition_by_dirs(tf_definitions)

        graphs: list[tuple[str, TerraformLocalGraph]] = []
        for source_path, dir_definitions in dirs_to_definitions.items():
            module, parsed_tf_definitions = self.parser.parse_hcl_module_from_multi_tf_definitions(dir_definitions, source_path, self.source)
            local_graph = TerraformLocalGraph(module)
            local_graph.build_graph(render_variables=render_variables)
            graphs.append((source_path, local_graph))

        return graphs
