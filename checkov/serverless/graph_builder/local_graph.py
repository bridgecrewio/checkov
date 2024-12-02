from typing import Any

from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.serverless.graph_builder.graph_components.blocks import ServerlessBlock


class ServerlessLocalGraph(LocalGraph[ServerlessBlock]):
    def __init__(self, definitions: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.vertices: list[ServerlessBlock] = []
        self.definitions = definitions
        self.vertices_by_path_and_id: dict[tuple[str, str], int] = {}
        self.vertices_by_name: dict[str, int] = {}