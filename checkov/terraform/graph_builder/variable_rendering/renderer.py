import re
from collections import Hashable
from copy import deepcopy
from typing import TYPE_CHECKING, List, Dict, Any, Tuple, Union, Optional

from lark.tree import Tree

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.utils import join_trimmed_strings
from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes, reserved_attribute_names
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.utils import (
    get_referenced_vertices_in_value,
    remove_index_pattern_from_str,
    attribute_has_nested_attributes,
)
from checkov.terraform.graph_builder.variable_rendering.vertex_reference import VertexReference
from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import replace_string_value, \
    evaluate_terraform

if TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

ATTRIBUTES_NO_EVAL = ["template_body", "template"]
VAR_TYPE_DEFAULT_VALUES = {
    'list': [],
    'map': {}
}
# matches the internal value of the 'type' attribute: usually like '${map}' or '${map(string)}', but could possibly just
# be like 'map' or 'map(string)' (but once we hit a ( or } we can stop)
TYPE_REGEX = re.compile(r'^(\${)?([a-z]+)')


class TerraformVariableRenderer(VariableRenderer):
    def __init__(self, local_graph: "TerraformLocalGraph") -> None:
        super().__init__(local_graph)

    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> None:
        multiple_edges = len(edge_list) > 1
        edge = edge_list[0]
        origin_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        val_to_eval = deepcopy(origin_vertex_attributes.get(edge.label, ""))

        referenced_vertices = get_referenced_vertices_in_value(
            value=val_to_eval, aliases={}, resources_types=self.local_graph.get_resources_types_in_graph()
        )
        if not referenced_vertices:
            origin_vertex = self.local_graph.vertices[edge.origin]
            destination_vertex = self.local_graph.vertices[edge.dest]
            if origin_vertex.block_type == BlockType.VARIABLE and destination_vertex.block_type == BlockType.MODULE:
                self.update_evaluated_value(
                    changed_attribute_key=edge.label,
                    changed_attribute_value=destination_vertex.attributes[origin_vertex.name],
                    vertex=edge.origin,
                    change_origin_id=edge.dest,
                    attribute_at_dest=edge.label,
                )
                return
            if (
                origin_vertex.block_type == BlockType.VARIABLE
                and destination_vertex.block_type == BlockType.TF_VARIABLE
            ):
                destination_vertex = list(filter(lambda v: v.block_type == BlockType.TF_VARIABLE, map(lambda e: self.local_graph.vertices[e.dest], edge_list)))[-1]  # evaluate the last specified variable based on .tfvars precedence
                self.update_evaluated_value(
                    changed_attribute_key=edge.label,
                    changed_attribute_value=destination_vertex.attributes["default"],
                    vertex=edge.origin,
                    change_origin_id=edge.dest,
                    attribute_at_dest=edge.label,
                )
                return

        modified_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        origin_val = modified_vertex_attributes.get(edge.label, "")
        val_to_eval = deepcopy(origin_val)
        first_key_path = None

        if referenced_vertices:
            for edge in edge_list:
                dest_vertex_attributes = self.local_graph.get_vertex_attributes_by_index(edge.dest, add_hash=False)
                key_path_in_dest_vertex, replaced_key = self.find_path_from_referenced_vertices(
                    referenced_vertices, dest_vertex_attributes
                )
                if not key_path_in_dest_vertex or not replaced_key:
                    continue
                if not first_key_path:
                    first_key_path = key_path_in_dest_vertex

                evaluated_attribute_value = self.extract_value_from_vertex(
                    key_path_in_dest_vertex, dest_vertex_attributes
                )
                if evaluated_attribute_value is not None:
                    val_to_eval = self.replace_value(edge, val_to_eval, replaced_key, evaluated_attribute_value, True)
                if not multiple_edges and val_to_eval != origin_val:
                    self.update_evaluated_value(
                        changed_attribute_key=edge.label,
                        changed_attribute_value=val_to_eval,
                        vertex=edge.origin,
                        change_origin_id=edge.dest,
                        attribute_at_dest=key_path_in_dest_vertex,
                    )

        if multiple_edges and val_to_eval != origin_val:
            self.update_evaluated_value(
                changed_attribute_key=edge.label,
                changed_attribute_value=val_to_eval,
                vertex=edge.origin,
                change_origin_id=edge.dest,
                attribute_at_dest=first_key_path,
            )

        # Avoid loops on output => output edges
        if (
            self.local_graph.vertices[edge.origin].block_type == BlockType.OUTPUT
            and self.local_graph.vertices[edge.dest].block_type == BlockType.OUTPUT
        ):
            if edge.origin not in self.done_edges_by_origin_vertex:
                self.done_edges_by_origin_vertex[edge.origin] = []
            self.done_edges_by_origin_vertex[edge.origin].append(edge)

    def extract_value_from_vertex(self, key_path: List[str], attributes: Dict[str, Any]) -> Any:
        for i, _ in enumerate(key_path):
            key = join_trimmed_strings(char_to_join=".", str_lst=key_path, num_to_trim=i)
            value = attributes.get(key, None)
            if value is not None:
                return value

        reversed_key_path = key_path[::-1]
        for i, _ in enumerate(reversed_key_path):
            key = join_trimmed_strings(char_to_join=".", str_lst=reversed_key_path, num_to_trim=i)
            value = attributes.get(key, None)
            if value is not None:
                return value

        if attributes.get(CustomAttributes.BLOCK_TYPE) in [BlockType.VARIABLE, BlockType.TF_VARIABLE]:
            var_type = attributes.get('type')
            default_val = attributes.get("default")
            if default_val is None:
                # this allows functions like merge(var.xyz, ...) to work even with no default value
                default_val = self.get_default_placeholder_value(var_type)
            value = None
            if isinstance(default_val, dict):
                value = self.extract_value_from_vertex(key_path, default_val)
            return default_val if not value else value
        if attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.OUTPUT:
            return attributes.get("value")
        return None

    @staticmethod
    def get_default_placeholder_value(var_type):
        if not var_type or type(var_type) != str:
            return None
        match = TYPE_REGEX.match(var_type)
        return VAR_TYPE_DEFAULT_VALUES.get(match.group(2)) if match else None

    @staticmethod
    def find_path_from_referenced_vertices(
        referenced_vertices: List[VertexReference], vertex_attributes: Dict[str, Any]
    ) -> Tuple[List[str], str]:
        """
        :param referenced_vertices: an array of VertexReference
        :param vertex_attributes: attributes to search
        :return attribute_path: [] if referenced_vertices does not contain vertex_attributes,
                                else the path to the searched attribute: ['vpc_id']
        :return origin_value
        """
        for vertex_reference in referenced_vertices:
            block_type = vertex_reference.block_type
            attribute_path = vertex_reference.sub_parts
            copy_of_attribute_path = attribute_path.copy()
            if vertex_attributes[CustomAttributes.BLOCK_TYPE] == block_type:
                for i, _ in enumerate(copy_of_attribute_path):
                    copy_of_attribute_path[i] = remove_index_pattern_from_str(copy_of_attribute_path[i])
                    name = ".".join(copy_of_attribute_path[: i + 1])
                    if vertex_attributes[CustomAttributes.BLOCK_NAME] == name:
                        return attribute_path, vertex_reference.origin_value
            elif block_type == BlockType.MODULE:
                copy_of_attribute_path.reverse()
                for i, _ in enumerate(copy_of_attribute_path):
                    copy_of_attribute_path[i] = remove_index_pattern_from_str(copy_of_attribute_path[i])
                    name = ".".join(copy_of_attribute_path[: i + 1])
                    if vertex_attributes[CustomAttributes.BLOCK_NAME] == name:
                        return name.split("."), vertex_reference.origin_value
        return [], ""

    def update_evaluated_value(
        self,
        changed_attribute_key: str,
        changed_attribute_value: Union[str, List[str]],
        vertex: int,
        change_origin_id: int,
        attribute_at_dest: Optional[Union[str, List[str]]] = None,
    ) -> None:
        """
        The function updates the value of changed_attribute_key with changed_attribute_value for vertex
        """
        str_to_evaluate = (
            str(changed_attribute_value)
            if changed_attribute_key in ATTRIBUTES_NO_EVAL
            else f'"{str(changed_attribute_value)}"'
        )
        str_to_evaluate = str_to_evaluate.replace("\\\\", "\\")
        evaluated_attribute_value = (
            str_to_evaluate if changed_attribute_key in ATTRIBUTES_NO_EVAL else evaluate_terraform(str_to_evaluate)
        )
        self.local_graph.update_vertex_attribute(
            vertex, changed_attribute_key, evaluated_attribute_value, change_origin_id, attribute_at_dest
        )

    def evaluate_vertices_attributes(self) -> None:
        for vertex in self.local_graph.vertices:
            decoded_attributes = vertex.get_attribute_dict(add_hash=False)
            for attr in decoded_attributes:
                if attr in vertex.changed_attributes:
                    continue
                origin_value = decoded_attributes[attr]
                if not isinstance(origin_value, str):
                    continue
                evaluated_attribute_value = evaluate_terraform(origin_value)
                if origin_value != evaluated_attribute_value:
                    vertex.update_inner_attribute(attr, vertex.attributes, evaluated_attribute_value)

    def replace_value(
        self,
        edge: Edge,
        original_val: List[Any],
        replaced_key: str,
        replaced_value: Any,
        keep_origin: bool,
        count: int = 0,
    ) -> Union[Any, List[Any]]:
        if count > 1:
            return original_val
        new_val = replace_string_value(
            original_str=original_val,
            str_to_replace=replaced_key,
            replaced_value=replaced_value,
            keep_origin=keep_origin,
        )
        return new_val

    def _render_variables_from_vertices(self) -> None:
        pass

    def evaluate_non_rendered_values(self) -> None:
        for vertex in self.local_graph.vertices:
            changed_attributes = {}
            attributes: Dict[str, Any] = {}
            vertex.get_origin_attributes(attributes)
            for attribute in filter(
                lambda attr: attr not in reserved_attribute_names
                and not attribute_has_nested_attributes(attr, vertex.attributes),
                vertex.attributes,
            ):
                curr_val = vertex.attributes.get(attribute)
                lst_curr_val = curr_val
                if not isinstance(lst_curr_val, list):
                    lst_curr_val = [lst_curr_val]
                if len(lst_curr_val) > 0 and isinstance(lst_curr_val[0], Tree):
                    lst_curr_val[0] = str(lst_curr_val[0])
                evaluated_lst = []
                for inner_val in lst_curr_val:
                    if (
                        isinstance(inner_val, str)
                        and not any(c in inner_val for c in ["{", "}", "[", "]", "="])
                        or attribute in ATTRIBUTES_NO_EVAL
                    ):
                        evaluated_lst.append(inner_val)
                        continue
                    evaluated = self.evaluate_value(inner_val)
                    evaluated_lst.append(evaluated)
                evaluated = evaluated_lst
                if not isinstance(curr_val, list):
                    evaluated = evaluated_lst[0]
                if evaluated != curr_val:
                    vertex.update_inner_attribute(attribute, vertex.attributes, evaluated)
                    changed_attributes[attribute] = evaluated
            self.local_graph.update_vertex_config(vertex, changed_attributes)

    def evaluate_value(self, val: Any) -> Any:
        if type(val) not in [str, list, set, dict]:
            evaluated_val = val
        elif isinstance(val, str):
            evaluated_val = evaluate_terraform(val, keep_interpolations=False)
        elif isinstance(val, list):
            evaluated_val = []
            for v in val:
                evaluated_val.append(self.evaluate_value(v))
        elif isinstance(val, set):
            evaluated_val = set()
            for v in val:
                evaluated_v = self.evaluate_value(v)
                if isinstance(evaluated_v, Hashable):
                    evaluated_val.add(evaluated_v)
                else:
                    evaluated_val.add(str(evaluated_v))
        else:
            evaluated_val = {}
            for k, v in val.items():
                evaluated_key = self.evaluate_value(k)
                evaluated_val[evaluated_key] = self.evaluate_value(v)
        return evaluated_val
