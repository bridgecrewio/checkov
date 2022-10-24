from __future__ import annotations

from typing import Type, Any

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_manager import GraphManager
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.kubernetes_utils import get_folder_definitions


class KubernetesGraphManager(GraphManager[KubernetesLocalGraph]):
    def __init__(self, db_connector: DBConnector, source: str = "Kubernetes") -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_classType: Type[KubernetesLocalGraph] = KubernetesLocalGraph,
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None
    ) -> tuple[KubernetesLocalGraph, dict[str, Any]]:
        definitions, definitions_raw = get_folder_definitions(source_dir, excluded_paths)
        local_graph = self.build_graph_from_definitions(definitions, False)
        return local_graph, definitions

    def build_graph_from_definitions(
        self, definitions: dict[str, Any], render_variables: bool = True
    ) -> KubernetesLocalGraph:
        local_graph = KubernetesLocalGraph(definitions)
        local_graph.build_graph(False)
        return local_graph
