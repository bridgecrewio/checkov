from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from checkov.arm.graph_builder.local_graph import ArmLocalGraph
from checkov.arm.utils import get_scannable_file_paths, get_files_definitions
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_manager import GraphManager

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraphConnector


class ArmGraphManager(GraphManager[ArmLocalGraph, "dict[str, dict[str, Any]]"]):
    def __init__(self, db_connector: LibraryGraphConnector, source: str = GraphSource.ARM) -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: type[ArmLocalGraph] = ArmLocalGraph,
        render_variables: bool = False,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
    ) -> tuple[ArmLocalGraph, dict[str, dict[str, Any]]]:
        file_paths = get_scannable_file_paths(root_folder=source_dir, excluded_paths=excluded_paths)
        filepath_fn = lambda f: f"/{os.path.relpath(f, os.path.commonprefix((source_dir, f)))}"
        definitions, _, _ = get_files_definitions(files=file_paths, filepath_fn=filepath_fn)

        local_graph = self.build_graph_from_definitions(definitions=definitions)

        return local_graph, definitions

    def build_graph_from_definitions(
        self, definitions: dict[str, dict[str, Any]], render_variables: bool = True
    ) -> ArmLocalGraph:
        local_graph = ArmLocalGraph(definitions=definitions)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
