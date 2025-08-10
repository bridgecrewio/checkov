from __future__ import annotations

import json
from ast import literal_eval
import logging
import os
import re
from collections.abc import Hashable, Sequence
from json import JSONDecodeError

import dpath
from typing import TYPE_CHECKING, List, Dict, Any, Tuple, Union, Optional, cast

from lark.tree import Tree

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.utils import join_trimmed_strings
from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer
from checkov.common.util.data_structures_utils import find_in_dict, pickle_deepcopy
from checkov.common.util.type_forcers import force_int
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes, reserved_attribute_names
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.utils import (
    get_attribute_is_leaf,
    get_referenced_vertices_in_value,
    remove_index_pattern_from_str,
    attribute_has_nested_attributes, attribute_has_dup_with_dynamic_attributes,
)
from checkov.terraform.graph_builder.variable_rendering.vertex_reference import VertexReference
import checkov.terraform.graph_builder.variable_rendering.evaluate_terraform as evaluator

if TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

VAR_TYPE_DEFAULT_VALUES: dict[str, list[Any] | dict[str, Any]] = {
    'list': [],
    'map': {}
}

attrsToFilterByResourceType = {
    "google_iam_workload_identity_pool_provider": ["attribute_condition"]
}

DYNAMIC_STRING = 'dynamic'
DYNAMIC_BLOCKS_LISTS = 'list'
DYNAMIC_BLOCKS_MAPS = 'map'
FOR_LOOP = 'for'
LOOKUP = 'lookup'
DOT_SEPERATOR = '.'
LEFT_BRACKET_WITH_QUOTATION = '["'
RIGHT_BRACKET_WITH_QUOTATION = '"]'
LEFT_PARENTHESIS = '('
COMMA = ','
LEFT_BRACKET = '['
RIGHT_BRACKET = ']'
LEFT_CURLY = '{'
RIGHT_CURLY = '}'
DOLLAR_PREFIX = '$'
FOR_EXPRESSION_DICT = ':>'
KEY_VALUE_SEPERATOR = ' : '

# matches the internal value of the 'type' attribute: usually like '${map}' or '${map(string)}', but could possibly just
# be like 'map' or 'map(string)' (but once we hit a ( or } we can stop)
TYPE_REGEX = re.compile(r'^(\${)?([a-z]+)')
CHECKOV_RENDER_MAX_LEN = force_int(os.getenv("CHECKOV_RENDER_MAX_LEN", "10000"))

DATA_SPECIAL_KEYWORDS = {
    "policy_data": "binding"
}


class TerraformVariableRenderer(VariableRenderer["TerraformLocalGraph"]):
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
        for e in edge_list:
            if not self.local_graph.vertices[e.origin] or not self.local_graph.vertices[e.dest]:
                return
        origin_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        val_to_eval = pickle_deepcopy(origin_vertex_attributes.get(edge.label, ""))

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
                self.update_evaluated_value(
                    changed_attribute_key=edge.label,
                    changed_attribute_value=destination_vertex.attributes['default'],
                    vertex=edge.origin,
                    change_origin_id=edge.dest,
                    attribute_at_dest=edge.label,
                )
                return

        modified_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        origin_val = modified_vertex_attributes.get(edge.label, "")
        val_to_eval = pickle_deepcopy(origin_val)
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
            special_key = DATA_SPECIAL_KEYWORDS.get(key, '')
            value = attributes.get(special_key)
            if attributes.get('block_type_') == BlockType.DATA and value is not None:
                return {special_key: value}

        if attributes.get(CustomAttributes.BLOCK_TYPE) in (BlockType.VARIABLE, BlockType.TF_VARIABLE):
            var_type = attributes.get('type')
            default_val = attributes.get("default")
            if default_val is None:
                # this allows functions like merge(var.xyz, ...) to work even with no default value
                default_val = self.get_default_placeholder_value(var_type)
            value = None
            if isinstance(default_val, dict):
                value = find_in_dict(input_dict=default_val, key_path=create_variable_key_path(key_path))
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
                    logging.debug(f"cannot evaluate this rendered value: {default_val}")
            return default_val if value is None else value
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
        referenced_vertices: Sequence[VertexReference], vertex_attributes: Dict[str, Any]
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
                    elif vertex_attributes[CustomAttributes.BLOCK_NAME] == name.replace(LEFT_BRACKET_WITH_QUOTATION, LEFT_BRACKET).replace(RIGHT_BRACKET_WITH_QUOTATION, RIGHT_BRACKET):
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
            str_to_evaluate if self.attributes_no_eval(changed_attribute_key, vertex) else evaluator.evaluate_terraform(str_to_evaluate)
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
                evaluated_attribute_value = evaluator.evaluate_terraform(origin_value)
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
        new_val = evaluator.replace_string_value(
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
                    try:
                        rendered_blocks = self._process_dynamic_blocks(dynamic_blocks)
                    except Exception:
                        logging.info(f'Failed to process dynamic blocks in file {vertex.path} of resource {vertex.name}'
                                     f' for blocks: {dynamic_blocks}')
                        continue
                    changed_attributes = []

                    for block_name, block_confs in rendered_blocks.items():
                        vertex.update_inner_attribute(block_name, vertex.attributes, block_confs)
                        changed_attributes.append(block_name)

                    self.local_graph.update_vertex_config(vertex, changed_attributes, True)

    @staticmethod
    def _extract_dynamic_arguments(block_name: str, block_content: Dict[str, Any], dynamic_arguments: List[str],
                                   path_accumulator: List[str]) -> None:
        dynamic_value_dot_ref = f"{block_name}.value"
        dynamic_value_bracket_ref = f'{block_name}["value"]'
        dynamic_value_refs = (dynamic_value_dot_ref, dynamic_value_bracket_ref)
        for argument, value in block_content.items():
            if value in dynamic_value_refs or isinstance(value, str) and dynamic_value_dot_ref in value:
                dynamic_arguments.append(DOT_SEPERATOR.join(filter(None, [*path_accumulator, argument])))
            elif isinstance(value, dict):
                TerraformVariableRenderer._extract_dynamic_arguments(block_name, value, dynamic_arguments,
                                                                     path_accumulator + [argument])

    @staticmethod
    def _process_dynamic_blocks(dynamic_blocks: list[dict[str, Any]] | dict[str, Any]) -> dict[
            str, list[dict[str, Any]] | dict[str, Any]]:
        rendered_blocks: dict[str, list[dict[str, Any]] | dict[str, Any]] = {}

        if not isinstance(dynamic_blocks, list) and not isinstance(dynamic_blocks, dict):
            logging.info(f"Dynamic blocks found, but of type {type(dynamic_blocks)}")

        dynamic_type = DYNAMIC_BLOCKS_LISTS
        if isinstance(dynamic_blocks, dict):
            dynamic_blocks = [dynamic_blocks]
            dynamic_type = DYNAMIC_BLOCKS_MAPS

        for block in dynamic_blocks:
            block_name, block_values = next(iter(block.items()))  # only one block per dynamic_block
            block_content = block_values.get("content")
            dynamic_values = block_values.get("for_each")
            dynamic_values = TerraformVariableRenderer._handle_for_loop_in_dynamic_values(dynamic_values)
            if not block_content or not dynamic_values or isinstance(dynamic_values, str):
                continue

            dynamic_arguments: list[str] = []
            TerraformVariableRenderer._extract_dynamic_arguments(block_name, block_content, dynamic_arguments, [])
            if not dynamic_arguments and len(dynamic_values) == 1:
                for argument, _ in block_content.items():
                    dynamic_arguments.append(argument)
            if dynamic_arguments and isinstance(dynamic_values, list):
                block_confs = []
                for dynamic_value in dynamic_values:
                    block_conf = pickle_deepcopy(block_content)
                    block_conf.pop(DYNAMIC_STRING, None)
                    for dynamic_argument in dynamic_arguments:
                        if dynamic_type == DYNAMIC_BLOCKS_MAPS:
                            if not isinstance(dynamic_value, dict):
                                continue
                            TerraformVariableRenderer._assign_dynamic_value_for_list(
                                dynamic_value=dynamic_value,
                                dynamic_argument=dynamic_argument,
                                block_conf=block_conf,
                                block_content=block_content,
                                block_name=block_name
                            )

                        else:
                            TerraformVariableRenderer._assign_dynamic_value_for_map(
                                dynamic_value=dynamic_value,
                                dynamic_argument=dynamic_argument,
                                block_conf=block_conf,
                                block_content=block_content,
                            )

                    block_confs.append(block_conf)
                rendered_blocks[block_name] = block_confs if len(block_confs) > 1 else block_confs[0]

            if DYNAMIC_STRING in block_content and dynamic_values:
                try:
                    next_key = next(iter(block_content[DYNAMIC_STRING].keys()))
                except (StopIteration, AttributeError):
                    continue
                block_content[DYNAMIC_STRING][next_key]['for_each'] = dynamic_values

                try:
                    flatten_key = next(iter(rendered_blocks.keys()))
                except StopIteration:
                    flatten_key = ''

                flatten_key_block = rendered_blocks.get(flatten_key)
                if isinstance(flatten_key_block, dict) and next_key in flatten_key_block:
                    flatten_key_block.update(TerraformVariableRenderer._process_dynamic_blocks(block_content[DYNAMIC_STRING]))
                elif isinstance(flatten_key_block, list) and isinstance(dynamic_values, list):
                    for i in range(len(flatten_key_block)):
                        block_content[DYNAMIC_STRING][next_key]['for_each'] = [dynamic_values[i]]
                        flatten_key_block[i].update(TerraformVariableRenderer._process_dynamic_blocks(block_content[DYNAMIC_STRING]))
                else:
                    rendered_blocks.update(TerraformVariableRenderer._process_dynamic_blocks(block_content[DYNAMIC_STRING]))

        return rendered_blocks

    @staticmethod
    def _assign_dynamic_value_for_list(
            dynamic_value: str | dict[str, Any] | dict[str, list[dict[str, dict[str, Any]]]],
            dynamic_argument: str,
            block_conf: dict[str, Any],
            block_content: dict[str, Any],
            block_name: str,
    ) -> None:
        dynamic_value_in_map = TerraformVariableRenderer.extract_dynamic_value_in_map(
            dpath.get(block_content, dynamic_argument, separator=DOT_SEPERATOR), dynamic_argument
        )
        if isinstance(dynamic_value, dict) and block_name not in dynamic_value and dynamic_value_in_map in dynamic_value:
            dpath.set(block_conf, dynamic_argument, dynamic_value[dynamic_value_in_map], separator=DOT_SEPERATOR)
        else:
            try:
                if DOT_SEPERATOR in dynamic_argument:
                    dynamic_args = dynamic_argument.split(DOT_SEPERATOR)
                    dpath.set(block_conf, dynamic_argument, dynamic_value[block_name][0][dynamic_args[0]][dynamic_args[1]], separator=DOT_SEPERATOR)  # type:ignore[index]
                else:
                    dpath.set(block_conf, dynamic_argument, dynamic_value[block_name][0][dynamic_value_in_map], separator=DOT_SEPERATOR)  # type:ignore[index]
            except (KeyError, IndexError):
                dynamic_content = block_content.get(dynamic_argument)
                if dynamic_content and LOOKUP in dynamic_content:
                    block_conf[dynamic_argument] = get_lookup_value(block_content, dynamic_argument)
                else:
                    return

    @staticmethod
    def _handle_for_loop_in_dynamic_values(dynamic_values: str | dict[str, Any]) -> str | dict[str, Any] | list[dict[str, Any]]:
        if not isinstance(dynamic_values, str):
            return dynamic_values

        if (dynamic_values.startswith(LEFT_BRACKET + FOR_LOOP) or dynamic_values.startswith(LEFT_BRACKET + " " + FOR_LOOP)) and dynamic_values.endswith(RIGHT_BRACKET):
            rendered_dynamic_values = dynamic_values[1:-1]
            start_bracket_idx = rendered_dynamic_values.find(LEFT_BRACKET)
            end_bracket_idx = find_match_bracket_index(rendered_dynamic_values, start_bracket_idx)
            if start_bracket_idx != -1 and end_bracket_idx != -1:
                rendered_dynamic_values = rendered_dynamic_values[start_bracket_idx:end_bracket_idx + 1].replace("'", '"')
            try:
                return cast("dict[str, Any] | list[dict[str, Any]]", json.loads(rendered_dynamic_values))
            except JSONDecodeError:
                return dynamic_values
        return dynamic_values

    @staticmethod
    def _assign_dynamic_value_for_map(
            dynamic_value: str | dict[str, Any],
            dynamic_argument: str,
            block_conf: dict[str, Any],
            block_content: dict[str, Any],
    ) -> None:
        if isinstance(dynamic_value, dict):
            if dynamic_argument in dynamic_value:
                dpath.set(block_conf, dynamic_argument, dynamic_value[dynamic_argument], separator=DOT_SEPERATOR)
            else:
                if isinstance(block_content, dict) and dynamic_argument in block_content and isinstance(block_content[dynamic_argument], str):
                    lookup_value = get_lookup_value(block_content, dynamic_argument)
                    dpath.set(block_conf, dynamic_argument, lookup_value, separator=DOT_SEPERATOR)
        else:
            dpath.set(block_conf, dynamic_argument, dynamic_value, separator=DOT_SEPERATOR)

    def shouldBeFilteredByConditionAndResourceType(self, attr: str, resource_type: List[str]) -> bool:
        if not resource_type:
            return False
        for resource in resource_type:
            if resource in attrsToFilterByResourceType and attr in attrsToFilterByResourceType[resource]:
                return True
        return False

    def evaluate_non_rendered_values(self) -> None:
        for index, vertex in enumerate(self.local_graph.vertices):
            changed_attributes = {}
            attributes: Dict[str, Any] = {}
            vertex.get_origin_attributes(attributes)
            attribute_is_leaf = get_attribute_is_leaf(vertex)
            filtered_attributes = [
                attr
                for attr in vertex.attributes
                if attr not in reserved_attribute_names and not attribute_has_nested_attributes(attr, vertex.attributes, attribute_is_leaf)
                and not attribute_has_dup_with_dynamic_attributes(attr, vertex.attributes)
                and not self.shouldBeFilteredByConditionAndResourceType(attr, vertex.attributes.get("resource_type", []))
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

    @staticmethod
    def extract_dynamic_value_in_map(dynamic_value: str, dynamic_argument: str = '') -> str:
        if LOOKUP in dynamic_value and dynamic_argument in dynamic_value:
            return dynamic_argument

        dynamic_value_in_map = dynamic_value.split(DOT_SEPERATOR)[-1]
        if LEFT_BRACKET not in dynamic_value_in_map:
            return dynamic_value_in_map
        return dynamic_value_in_map.split(LEFT_BRACKET_WITH_QUOTATION)[-1].replace(RIGHT_BRACKET_WITH_QUOTATION, '')

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
            evaluated_val = evaluator.evaluate_terraform(val, keep_interpolations=False)
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


def find_match_bracket_index(s: str, open_bracket_idx: int) -> int:
    res = {}
    pstack = []
    for i, c in enumerate(s):
        if c == LEFT_BRACKET:
            pstack.append(i)
        elif c == RIGHT_BRACKET:
            if len(pstack) == 0:
                logging.debug("No matching closing brackets at: " + str(i))
                return -1
            res[pstack.pop()] = i

    if len(pstack) > 0:
        logging.debug("No matching opening brackets at: " + str(pstack.pop()))

    return res.get(open_bracket_idx) or -1


def get_lookup_value(block_content: dict[str, Any], dynamic_argument: str) -> str:
    lookup_value: str = ''
    if 'None' in block_content[dynamic_argument]:
        lookup_value = 'null'
    elif 'False' in block_content[dynamic_argument]:
        lookup_value = 'false'
    elif 'True' in block_content[dynamic_argument]:
        lookup_value = 'true'
    return lookup_value


def create_variable_key_path(key_path: list[str]) -> str:
    """Returns the key_path without the var prefix

    ex.
    ["var", "properties", "region"] -> "properties/region"
    """
    return "/".join(key_path[1:])
