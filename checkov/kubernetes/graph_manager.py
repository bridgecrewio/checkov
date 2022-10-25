from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.common.graph.db_connectors.db_connector import DBConnector
from checkov.common.graph.graph_manager import GraphManager
from checkov.kubernetes.graph_builder.local_graph import KubernetesLocalGraph
from checkov.kubernetes.kubernetes_utils import get_folder_definitions, K8sGraphFlags

if TYPE_CHECKING:
    from networkx import DiGraph


class KubernetesGraphManager(GraphManager[KubernetesLocalGraph, "dict[str, list[dict[str, Any]]]"]):
    def __init__(self, db_connector: DBConnector[DiGraph], source: str = "Kubernetes") -> None:
        super().__init__(db_connector=db_connector, parser=None, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        local_graph_classType: type[KubernetesLocalGraph] = KubernetesLocalGraph,
        render_variables: bool = True,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        excluded_paths: list[str] | None = None,
        graph_flags: K8sGraphFlags | None = None
    ) -> tuple[KubernetesLocalGraph, dict[str, list[dict[str, Any]]]]:
        definitions, definitions_raw = get_folder_definitions(source_dir, excluded_paths)
        local_graph = self.build_graph_from_definitions(definitions=definitions, render_variables=False, graph_flags=graph_flags)
        return local_graph, definitions

    def build_graph_from_definitions(
        self, definitions: dict[str, list[dict[str, Any]]], render_variables: bool = True, graph_flags: K8sGraphFlags | None = None
    ) -> KubernetesLocalGraph:
        local_graph = KubernetesLocalGraph(definitions)
        if graph_flags is None:
            graph_flags = K8sGraphFlags()
        local_graph.build_graph(render_variables=False, graph_flags=graph_flags)
        return local_graph
