from __future__ import annotations

import logging
import os
from typing import Type, Any, TYPE_CHECKING, overload, Optional

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
        parsing_errors: Optional[dict[str, Exception]] = None,
        download_external_modules: Optional[bool] = False,
        excluded_paths: Optional[list[str]] = None,
        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
        vars_files: list[str] | None = None,
        external_modules_content_cache: Optional[dict[str, Any]] = None,
    ) -> tuple[list[tuple[TerraformLocalGraph, list[dict[TFDefinitionKey, dict[str, Any]]], str]], dict[str, str]]:
        logging.info("Parsing HCL files in source dir to multi graph")
        modules_with_definitions = self.parser.parse_multi_graph_hcl_module(
            source_dir=source_dir,
            source=self.source,
            download_external_modules=download_external_modules,
            external_modules_download_path=external_modules_download_path,
            parsing_errors=parsing_errors,
            excluded_paths=excluded_paths,
            vars_files=vars_files,
            external_modules_content_cache=external_modules_content_cache
        )

        graphs: list[tuple[TerraformLocalGraph, list[dict[TFDefinitionKey, dict[str, Any]]], str]] = []
        resource_subgraph_map: dict[str, str] = {}
        for module, tf_definitions in modules_with_definitions:
            logging.info("Building graph from parsed module")
            local_graph = local_graph_class(module)
            local_graph.build_graph(render_variables=render_variables)
            subgraph_abs_path = module.source_dir
            subgraph_path = subgraph_abs_path[subgraph_abs_path.rindex(source_dir) + len(source_dir) + 1:]
            graphs.append((local_graph, tf_definitions, subgraph_path))
            self.update_resource_subgraph_map(local_graph, subgraph_path, resource_subgraph_map, source_dir)
        return graphs, resource_subgraph_map

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: Type[TerraformLocalGraph] = TerraformLocalGraph,
        render_variables: bool = True,
        parsing_errors: Optional[dict[str, Exception]] = None,
        download_external_modules: Optional[bool] = False,
        excluded_paths: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> tuple[TerraformLocalGraph, dict[TFDefinitionKey, dict[str, Any]]]:
        logging.info("Parsing HCL files in source dir to graph")
        module, tf_definitions = self.parser.parse_hcl_module(
            source_dir=source_dir,
            source=self.source,
            download_external_modules=download_external_modules,
            external_modules_download_path=kwargs.get('external_modules_download_path', DEFAULT_EXTERNAL_MODULES_DIR),
            parsing_errors=parsing_errors,
            excluded_paths=excluded_paths,
            vars_files=kwargs.get('vars_files', None),
            external_modules_content_cache=kwargs.get('external_modules_content_cache', None)
        )

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

    def build_multi_graph_from_definitions(
        self,
        definitions: dict[TFDefinitionKey, dict[str, Any]],
        render_variables: bool = True,
    ) -> list[tuple[Optional[str], TerraformLocalGraph]]:
        module, tf_definitions = self.parser.parse_hcl_module_from_tf_definitions(definitions, "", self.source)
        dirs_to_definitions = self.parser.create_definition_by_dirs(tf_definitions)

        graphs: list[tuple[Optional[str], TerraformLocalGraph]] = []
        for source_path, dir_definitions in dirs_to_definitions.items():
            module, parsed_tf_definitions = self.parser.parse_hcl_module_from_multi_tf_definitions(dir_definitions, source_path, self.source)
            local_graph = TerraformLocalGraph(module)
            local_graph.build_graph(render_variables=render_variables)
            graphs.append((source_path, local_graph))

        return graphs

    @staticmethod
    def update_resource_subgraph_map(
            local_graph: TerraformLocalGraph, subgraph_path: str, resource_subgraph_map: dict[str, str], source_dir: str
    ) -> None:
        for v in local_graph.vertices:
            resource_id = f"/{os.path.relpath(v.path, source_dir)}:{v.id}"
            resource_subgraph_map[resource_id] = subgraph_path
