from typing import Any, List, Dict, Tuple, Union

from checkov.common.graph.graph_builder.local_graph import LocalGraph, _Block
from checkov.serverless.graph_builder.graph_components.blocks import ServerlessBlock


class ServerlessLocalGraph(LocalGraph[ServerlessBlock]):
    def __init__(self, definitions: Dict[str, Dict[str, Any]]) -> None:
        super().__init__()
        self.vertices: List[ServerlessBlock] = []
        self.definitions = definitions
        self.vertices_by_path_and_id: Dict[Tuple[str, str], int] = {}
        self.vertices_by_name: Dict[str, int] = {}

    def get_resources_types_in_graph(self) -> List[str]:
        pass

    @staticmethod
    def update_vertex_config(vertex: _Block, changed_attributes: Union[List[str], Dict[str, Any]],
                             has_dynamic_blocks: bool = False) -> None:
        pass

    def update_vertices_configs(self) -> None:
        pass

    def build_graph(self, render_variables: bool) -> None:
        pass



