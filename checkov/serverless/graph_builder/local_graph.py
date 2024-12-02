from typing import Any, List, Dict, Tuple

from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.serverless.graph_builder.graph_components.blocks import ServerlessBlock


class ServerlessLocalGraph(LocalGraph[ServerlessBlock]):
    def __init__(self, definitions: Dict[str, Dict[str, Any]]) -> None:
        super().__init__()
        self.vertices: List[ServerlessBlock] = []
        self.definitions = definitions
        self.vertices_by_path_and_id: Dict[Tuple[str, str], int] = {}
        self.vertices_by_name: Dict[str, int] = {}
