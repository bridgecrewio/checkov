from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from checkov.arm.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.utils import adjust_value
from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer
from checkov.common.util.data_structures_utils import pickle_deepcopy

if TYPE_CHECKING:
    from checkov.arm.graph_builder.local_graph import ArmLocalGraph


class ArmVariableRenderer(VariableRenderer["ArmLocalGraph"]):
    def __init__(self, local_graph: ArmLocalGraph) -> None:
        super().__init__(local_graph)

    def _render_variables_from_vertices(self) -> None:
        # need to add rendering to function like format, reference etc
        pass

    def evaluate_vertex_attribute_from_edge(self, edge_list: list[Edge]) -> None:
        origin_vertex_attributes = self.local_graph.vertices[edge_list[0].origin].attributes
        value_to_eval = pickle_deepcopy(origin_vertex_attributes.get(edge_list[0].label, ""))
        attr_path = None
        for edge in edge_list:
            attr_path, attr_value = self.extract_dest_attribute_path_and_value(dest_index=edge.dest,
                                                                               origin_value=value_to_eval)
            if not attr_value:
                continue

            '''if the arg start with '[parameters'/ '[variables' its mean we need to eval the all attribute
            like here - "addressPrefix": "[parameters('subnetAddressPrefix')]" '''
            if len(edge_list) == 1 and isinstance(value_to_eval, str) and value_to_eval.startswith(("[parameters", "[variables")):
                value_to_eval = attr_value
                continue
            '''
            if the value i need to eval is part of the full attribute like "[format('{0}/{1}', parameters('vnetName'), variables('subnetName'))]"
            or "[resourceId('Microsoft.Network/networkProfiles', variables('networkProfileName'))]".
            vertices[edge.dest].id = variables.networkProfileName -> variables('networkProfileName')
            '''
            val_to_replace = self.local_graph.vertices[edge.dest].id.replace(".", "('") + "')"
            if attr_value and isinstance(value_to_eval, str):
                value_to_eval = value_to_eval.replace(val_to_replace, str(attr_value))

        self.local_graph.update_vertex_attribute(
            vertex_index=edge_list[0].origin,
            attribute_key=edge_list[0].label,
            attribute_value=value_to_eval,
            change_origin_id=edge_list[0].dest,
            attribute_at_dest=attr_path,
        )

    def extract_dest_attribute_path_and_value(self, dest_index: int, origin_value: Any) -> tuple[str, Any] | tuple[None, None]:
        vertex = self.local_graph.vertices[dest_index]
        if vertex.block_type == BlockType.PARAMETER:
            new_value = vertex.attributes.get("defaultValue")
            if new_value:
                new_value = adjust_value(element_name=origin_value, value=new_value)
                return "defaultValue", new_value
            else:
                logging.warning(f'No defaultValue for parameter id = {vertex.id}')
                return "defaultValue", None
        elif vertex.block_type == BlockType.VARIABLE:
            new_value = adjust_value(element_name=origin_value, value=vertex.attributes.get("value"))
            return "value", new_value
        return None, None

    def evaluate_non_rendered_values(self) -> None:
        pass
