from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from typing import List, Dict, Callable, Union, Any, Set, Iterable, TypeVar, Generic, TYPE_CHECKING

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder.graph_resources_encription_manager import GraphResourcesEncryptionManager
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder import Edge
    from checkov.common.graph.graph_builder.graph_components.blocks import Block  # noqa

_Block = TypeVar("_Block", bound="Block")


class LocalGraph(Generic[_Block]):
    def __init__(self) -> None:
        self.vertices: List[_Block] = []
        self.edges: List[Edge] = []
        self.in_edges: Dict[int, List[Edge]] = defaultdict(list)  # map between vertex index and the edges entering it
        self.out_edges: Dict[int, List[Edge]] = defaultdict(list)  # map between vertex index and the edges exiting it
        self.vertices_by_block_type: Dict[str, List[int]] = defaultdict(list)
        self.vertex_hash_cache: Dict[int, str] = defaultdict(str)
        self.vertices_block_name_map: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: defaultdict(list))
        self._graph_resource_encryption_manager = GraphResourcesEncryptionManager()

    @abstractmethod
    def build_graph(self, render_variables: bool) -> None:
        pass

    def get_vertices_with_degrees_conditions(
        self, out_degree_cond: Callable[[int], bool], in_degree_cond: Callable[[int], bool]
    ) -> Set[int]:
        vertices_with_out_degree = {
            vertex_index for vertex_index, vertex_value in self.out_edges.items() if out_degree_cond(len(vertex_value))
        }
        vertices_with_in_degree = {
            vertex_index for vertex_index, vertex_value in self.in_edges.items() if in_degree_cond(len(vertex_value))
        }

        return vertices_with_in_degree.intersection(vertices_with_out_degree)

    def get_in_edges(self, end_vertices: Iterable[int]) -> List[Edge]:
        res = []
        for vertex in end_vertices:
            res.extend(self.in_edges.get(vertex, []))
        return self.sort_edged_by_dest_out_degree(res)

    def get_in_edges_deduped(self, end_vertices: Iterable[int]) -> Set[Edge]:
        res = set()
        for vertex in end_vertices:
            res.update(self.in_edges.get(vertex, []))
        return res

    def sort_edged_by_dest_out_degree(self, edges: Iterable[Edge]) -> List[Edge]:
        edged_by_out_degree: Dict[int, List[Edge]] = {}
        for edge in edges:
            dest_out_degree = len(self.out_edges[edge.dest])
            edged_by_out_degree.setdefault(dest_out_degree, []).append(edge)
        sorted_edges = []
        for degree in sorted(edged_by_out_degree.keys()):
            sorted_edges.extend(edged_by_out_degree[degree])
        return sorted_edges

    @abstractmethod
    def update_vertices_configs(self) -> None:
        pass

    @staticmethod
    @abstractmethod
    def update_vertex_config(vertex: _Block, changed_attributes: Union[List[str], Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def get_resources_types_in_graph(self) -> List[str]:
        pass

    def get_vertex_attributes_by_index(self, index: int, add_hash: bool = True) -> Dict[str, Any]:
        return self.vertices[index].get_attribute_dict(add_hash)

    def update_vertex_attribute(
        self,
        vertex_index: int,
        attribute_key: str,
        attribute_value: Any,
        change_origin_id: int,
        attribute_at_dest: str,
        transform_step: bool = False
    ) -> None:
        previous_breadcrumbs = []
        if attribute_at_dest:
            previous_breadcrumbs = self.vertices[change_origin_id].changed_attributes.get(attribute_at_dest, [])
        self.vertices[vertex_index].update_attribute(
            attribute_key, attribute_value, change_origin_id, previous_breadcrumbs, attribute_at_dest, transform_step
        )

    def calculate_encryption_attribute(self, encription_by_resource_type: Dict[str, Any]) -> None:
        self._graph_resource_encryption_manager.set_encription_by_resource_type(encription_by_resource_type)
        for vertex_index in self.vertices_by_block_type.get(BlockType.RESOURCE, []):
            vertex = self.vertices[vertex_index]
            encryption_result = self._graph_resource_encryption_manager.get_encryption_result(vertex)
            if not encryption_result:
                continue
            vertex.attributes[CustomAttributes.ENCRYPTION] = encryption_result.encrypted
            vertex.attributes[CustomAttributes.ENCRYPTION_DETAILS] = encryption_result.reason
