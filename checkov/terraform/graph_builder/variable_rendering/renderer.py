from __future__ import annotations

from ast import literal_eval
import logging
import os
import re
from collections.abc import Hashable
from copy import deepcopy
from typing import TYPE_CHECKING, List, Dict, Any, Tuple, Union, Optional

from lark.tree import Tree

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.utils import join_trimmed_strings
from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer
from checkov.common.util.type_forcers import force_int
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes, reserved_attribute_names
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

VAR_TYPE_DEFAULT_VALUES: dict[str, list[Any] | dict[str, Any]] = {
    'list': [],
    'map': {}
}
# matches the internal value of the 'type' attribute: usually like '${map}' or '${map(string)}', but could possibly just
# be like 'map' or 'map(string)' (but once we hit a ( or } we can stop)
TYPE_REGEX = re.compile(r'^(\${)?([a-z]+)')
CHECKOV_RENDER_MAX_LEN = force_int(os.getenv("CHECKOV_RENDER_MAX_LEN", "10000"))


class TerraformVariableRenderer(VariableRenderer):
    def __init__(self, local_graph: "TerraformLocalGraph") -> None:
        super().__init__(local_graph)

    def attributes_no_eval(self, attribute: str, vertex_index: int) -> bool:
        """
        Check if the attribute should not be evaluated.
        :param attribute: the attribute to check
        :param vertex_index: the index of the current vertex
        :return bool: True if the attribute should not be evaluated and False otherwise
        """
        if attribute in {"template_body", "template"}:
            return True

        # OCI policy statements have a special syntax and should not be evaluated.
        # Check if the vertex at this index is an OCI terraform resource.
        if attribute == "statements":
            vertex_attributes = self.local_graph.get_vertex_attributes_by_index(vertex_index)
            if vertex_attributes and vertex_attributes.get("resource_type", "").startswith("oci_"):
                return True

        return False

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

        if attributes.get(CustomAttributes.BLOCK_TYPE) in (BlockType.VARIABLE, BlockType.TF_VARIABLE):
            var_type = attributes.get('type')
            default_val = attributes.get("default")
            if default_val is None:
                # this allows functions like merge(var.xyz, ...) to work even with no default value
                default_val = self.get_default_placeholder_value(var_type)
            value = None
            if isinstance(default_val, dict):
                value = self.extract_value_from_vertex(key_path, default_val)
            elif (
                isinstance(var_type, str)
                and var_type.startswith("${object")
                and isinstance(default_val, str)
            ):
                try:
                    default_val_eval = literal_eval(default_val)
                    if isinstance(default_val_eval, dict):
                        value = self.extract_value_from_vertex(key_path, default_val_eval)
                except Exception:
                    logging.debug(f"cant evaluate this rendered value: {default_val}")
            return default_val if not value else value
        if attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.OUTPUT:
            return attributes.get("value")
        return None

    @staticmethod
    def get_default_placeholder_value(var_type: Any) -> list[Any] | dict[str, Any] | None:
        if not var_type or not isinstance(var_type, str):
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
            if self.attributes_no_eval(changed_attribute_key, vertex)
            else f'"{str(changed_attribute_value)}"'
        )
        str_to_evaluate = str_to_evaluate.replace("\\\\", "\\")
        evaluated_attribute_value = (
            str_to_evaluate if self.attributes_no_eval(changed_attribute_key, vertex) else evaluate_terraform(str_to_evaluate)
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
        self._render_dynamic_blocks()

    def _render_dynamic_blocks(self) -> None:
        vertex_indices = self.local_graph.vertices_by_block_type[BlockType.RESOURCE]

        for idx in vertex_indices:
            vertex = self.local_graph.vertices[idx]
            if vertex.has_dynamic_block:
                # only check dynamic blocks on the root level for now
                dynamic_blocks = vertex.attributes.get("dynamic")
                if dynamic_blocks:
                    rendered_blocks = self._process_dynamic_blocks(dynamic_blocks)
                    changed_attributes = []

                    for block_name, block_confs in rendered_blocks.items():
                        vertex.update_inner_attribute(block_name, vertex.attributes, block_confs)
                        changed_attributes.append(block_name)

                    self.local_graph.update_vertex_config(vertex, changed_attributes)

    @staticmethod
    def _process_dynamic_blocks(dynamic_blocks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        rendered_blocks: dict[str, list[dict[str, Any]]] = {}

        if not isinstance(dynamic_blocks, list):
            logging.info(f"Dynamic blocks found, but of type {type(dynamic_blocks)}")
            return rendered_blocks

        for block in dynamic_blocks:
            block_name, block_values = next(iter(block.items()))  # only one block per dynamic_block
            block_content = block_values.get("content")
            dynamic_values = block_values.get("for_each")
            if not block_content or not dynamic_values:
                return rendered_blocks

            dynamic_value_ref = f"{block_name}.value"
            dynamic_arguments = [
                argument
                for argument, value in block_content.items()
                if value == dynamic_value_ref
            ]
            if dynamic_arguments:
                block_confs = []
                for dynamic_value in dynamic_values:
                    block_conf = deepcopy(block_content)
                    for dynamic_argument in dynamic_arguments:
                        block_conf[dynamic_argument] = dynamic_value

                    block_confs.append(block_conf)
                rendered_blocks[block_name] = block_confs

        return rendered_blocks

    def evaluate_non_rendered_values(self) -> None:
        for index, vertex in enumerate(self.local_graph.vertices):
            changed_attributes = {}
            attributes: Dict[str, Any] = {}
            vertex.get_origin_attributes(attributes)
            filtered_attributes = [
                attr
                for attr in vertex.attributes
                if attr not in reserved_attribute_names and not attribute_has_nested_attributes(attr, vertex.attributes)
            ]
            for attribute in filtered_attributes:
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
                        and not any(c in inner_val for c in ("{", "}", "[", "]", "="))
                        or self.attributes_no_eval(attribute, index)
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
        val_length: int = len(str(val))
        if CHECKOV_RENDER_MAX_LEN and 0 < CHECKOV_RENDER_MAX_LEN < val_length:
            logging.debug(f'Rendering was skipped for a {val_length}-character-long string. If you wish to have it '
                          f'evaluated, please set the environment variable CHECKOV_RENDER_MAX_LEN '
                          f'to {str(val_length + 1)} or to 0 to allow rendering of any length')
            return val
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
