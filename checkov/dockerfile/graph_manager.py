from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_manager import GraphManager
from checkov.dockerfile.graph_builder.local_graph import DockerfileLocalGraph
from checkov.dockerfile.utils import get_scannable_file_paths, get_files_definitions

if TYPE_CHECKING:
    from checkov.common.typing import LibraryGraphConnector
    from dockerfile_parse.parser import _Instruction  # only in extra_stubs


class DockerfileGraphManager(GraphManager[DockerfileLocalGraph, "dict[str, dict[str, list[_Instruction]]]"]):
    def __init__(self, db_connector: LibraryGraphConnector, source: str = GraphSource.DOCKERFILE) -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_class: type[DockerfileLocalGraph] = DockerfileLocalGraph,
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
        **kwargs: Any,
    ) -> tuple[DockerfileLocalGraph, dict[str, dict[str, list[_Instruction]]]]:
        file_paths = get_scannable_file_paths(root_folder=source_dir, excluded_paths=excluded_paths)
        filepath_fn = lambda f: f"/{os.path.relpath(f, os.path.commonprefix((source_dir, f)))}"
        definitions, _ = get_files_definitions(files=file_paths, filepath_fn=filepath_fn)

        local_graph = self.build_graph_from_definitions(definitions=definitions)

        return local_graph, definitions

    def build_graph_from_definitions(
        self,
        definitions: dict[str, dict[str, list[_Instruction]]],
        render_variables: bool = False,
    ) -> DockerfileLocalGraph:
        local_graph = DockerfileLocalGraph(definitions=definitions)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
