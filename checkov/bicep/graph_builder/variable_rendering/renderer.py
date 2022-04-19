from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from pycep.transformer import BicepElement

from checkov.bicep.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer

if TYPE_CHECKING:
    from checkov.bicep.graph_builder.local_graph import BicepLocalGraph


class BicepVariableRenderer(VariableRenderer):
    def __init__(self, local_graph: BicepLocalGraph) -> None:
        super().__init__(local_graph)

    def _render_variables_from_vertices(self) -> None:
        pass

    def evaluate_vertex_attribute_from_edge(self, edge_list: list[Edge]) -> None:
        edge = edge_list[0]
        origin_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        val_to_eval = deepcopy(origin_vertex_attributes.get(edge.label, ""))

        attr_path, attr_value = self.extract_dest_attribute_path_and_value(dest_index=edge.dest, origin_value=val_to_eval)

        if attr_path:
            self.local_graph.update_vertex_attribute(
                vertex_index=edge.origin,
                attribute_key=edge.label,
                attribute_value=attr_value,
                change_origin_id=edge.dest,
                attribute_at_dest=attr_path,
            )

    def extract_dest_attribute_path_and_value(self, dest_index: int, origin_value: Any) -> tuple[str, Any] | tuple[None, None]:
        if isinstance(origin_value, BicepElement):
            vertex = self.local_graph.vertices[dest_index]

            if vertex.block_type == BlockType.PARAM:
                default = vertex.attributes.get("default")
                if default:
                    return "default", default

        return None, None
