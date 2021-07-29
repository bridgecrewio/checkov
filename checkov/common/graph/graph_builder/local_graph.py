from abc import abstractmethod
from collections import defaultdict
from typing import List, Dict

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder.graph_components.blocks import Block


class LocalGraph:
    def __init__(self) -> None:
        self.vertices: List[Block] = []
        self.edges: List[Edge] = []
        self.in_edges: Dict[int, List[Edge]] = defaultdict(list)  # map between vertex index and the edges entering it
        self.out_edges: Dict[int, List[Edge]] = defaultdict(list)  # map between vertex index and the edges exiting it
        self.vertices_by_block_type: Dict[str, List[int]] = defaultdict(list)
        self.vertex_hash_cache: Dict[int, str] = defaultdict(str)
        self.vertices_block_name_map: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))

    @abstractmethod
    def build_graph(self, render_variables: bool) -> None:
        pass
