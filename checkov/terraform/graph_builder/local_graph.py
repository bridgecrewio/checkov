from __future__ import annotations

import logging
import os
from collections import defaultdict
from functools import partial
from pathlib import Path
from typing import List, Optional, Union, Any, Dict, overload, TypedDict

import checkov.terraform.graph_builder.foreach.consts
from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder import reserved_attribute_names
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.graph.graph_builder.utils import calculate_hash, join_trimmed_strings, filter_sub_keys
from checkov.common.runners.base_runner import strtobool
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.type_forcers import force_int
from checkov.terraform.graph_builder.foreach.builder import ForeachBuilder
from checkov.terraform.graph_builder.variable_rendering.vertex_reference import TerraformVertexReference
from checkov.terraform.modules.module_objects import TFModule
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.graph_builder.utils import (
    get_attribute_is_leaf,
    get_referenced_vertices_in_value,
    attribute_has_nested_attributes,
    remove_index_pattern_from_str,
    join_double_quote_surrounded_dot_split,
)
from checkov.terraform.graph_builder.utils import is_local_path
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer


MODULE_RESERVED_ATTRIBUTES = ("source", "version")
CROSS_VARIABLE_EDGE_PREFIX = '[cross-variable] '


class Undetermined(TypedDict):
    module_vertex_id: int
    attribute_name: str
    variable_vertex_id: int


class TerraformLocalGraph(LocalGraph[TerraformBlock]):
    def __init__(self, module: Module) -> None:
        super().__init__()
        self.vertices: list[TerraformBlock] = []
        self.module = module
        self.map_path_to_module: Dict[str, List[int]] = {}
        self.relative_paths_cache: dict[tuple[str, str], str] = {}
        self.abspath_cache: Dict[str, str] = {}
        self.dirname_cache: Dict[str, str] = {}
        self.vertices_by_module_dependency_by_name: Dict[TFModule | None, Dict[str, Dict[str, List[int]]]] = defaultdict(partial(defaultdict, partial(defaultdict, list)))  # type:ignore[arg-type]
        self.vertices_by_module_dependency: Dict[TFModule | None, Dict[str, List[int]]] = defaultdict(partial(defaultdict, list))  # type:ignore[arg-type]
        self.enable_foreach_handling = strtobool(os.getenv('CHECKOV_ENABLE_FOREACH_HANDLING', 'True'))
        self.enable_modules_foreach_handling = strtobool(os.getenv('CHECKOV_ENABLE_MODULES_FOREACH_HANDLING', 'True'))
        self.foreach_blocks: Dict[str, List[int]] = {BlockType.RESOURCE: [], BlockType.MODULE: []}

    def build_graph(self, render_variables: bool) -> None:
        self._create_vertices()
        logging.info(f"[TerraformLocalGraph] created {len(self.vertices)} vertices")
        self._build_edges()
        logging.info(f"[TerraformLocalGraph] created {len(self.edges)} edges")
        if (self.enable_foreach_handling or self.enable_modules_foreach_handling) \
                and (self.foreach_blocks[BlockType.RESOURCE] or self.foreach_blocks[BlockType.MODULE]):
            try:
                logging.info('[TerraformLocalGraph] start handling foreach')
                foreach_builder = ForeachBuilder(self)
                foreach_builder.handle(self.foreach_blocks)
                self._arrange_graph_data()
                self._build_edges()
                logging.info(f"[TerraformLocalGraph] finished handling foreach values with {len(self.vertices)} vertices and {len(self.edges)} edges")
            except Exception as e:
                logging.info(f'Failed to process foreach handling, error: {str(e)}')

        self.calculate_encryption_attribute(ENCRYPTION_BY_RESOURCE_TYPE)
        if render_variables:
            logging.info(f"Rendering variables, graph has {len(self.vertices)} vertices and {len(self.edges)} edges")
            renderer = TerraformVariableRenderer(self)
            renderer.render_variables_from_local_graph()
            self.update_vertices_fields()
            if strtobool(os.getenv("CHECKOV_EXPERIMENTAL_CROSS_VARIABLE_EDGES", "True")):
                # experimental flag on building cross variable edges for terraform graph
                logging.info("Building cross variable edges")
                edges_count = len(self.edges)
                self._build_cross_variable_edges()
                logging.info(f"Found {len(self.edges) - edges_count} cross variable edges")
        else:
            self.update_vertices_fields()

    def update_vertices_fields(self) -> None:
        # Important to keep those 2 functions together, as the first affects the calculation of the second
        self._update_vertices_breadcrumbs_and_module_connections()
        self._update_nested_modules_address()

    def _create_vertices(self) -> None:
        logging.info("Creating vertices")
        self.vertices = [None] * len(self.module.blocks)  # type:ignore[list-item]  # are correctly set in the next lines
        for i, block in enumerate(self.module.blocks):
            self.vertices[i] = block
            self._add_block_data_to_graph(i, block)
            if self.enable_foreach_handling and (
                    checkov.terraform.graph_builder.foreach.consts.FOREACH_STRING in block.attributes or checkov.terraform.graph_builder.foreach.consts.COUNT_STRING in block.attributes) \
                    and block.block_type in (BlockType.MODULE, BlockType.RESOURCE):
                self.foreach_blocks[block.block_type].append(i)

    def _add_block_data_to_graph(self, idx: int, block: TerraformBlock) -> None:
        self.vertices_by_block_type[block.block_type].append(idx)
        self.vertices_block_name_map[block.block_type][block.name].append(idx)

        if block.block_type == BlockType.MODULE:
            # map between file paths and module vertices indexes from that file
            self.map_path_to_module.setdefault(block.path, []).append(idx)

        self.vertices_by_module_dependency[block.source_module_object][block.block_type].append(idx)
        self.vertices_by_module_dependency_by_name[block.source_module_object][block.block_type][block.name].append(idx)

        self.in_edges[idx] = []
        self.out_edges[idx] = []

    def _arrange_graph_data(self) -> None:
        # reset all the relevant data
        self.vertices_by_block_type = defaultdict(list)
        self.vertices_block_name_map = defaultdict(partial(defaultdict, list))  # type:ignore[arg-type]
        self.map_path_to_module = {}
        self.vertices_by_module_dependency = defaultdict(partial(defaultdict, list))  # type:ignore[arg-type]
        self.vertices_by_module_dependency_by_name = defaultdict(partial(defaultdict, partial(defaultdict, list)))  # type:ignore[arg-type]
        self.edges = []
        for i in range(len(self.vertices)):
            self.out_edges[i] = []
            self.in_edges[i] = []

        for i, block in enumerate(self.vertices):
            self._add_block_data_to_graph(i, block)

    def _get_aliases(self) -> Dict[str, Dict[str, str]]:
        """
        :return aliases: map between alias names that are found inside the blocks and the block type their aliased to.
        """
        return {
            vertex.name: {CustomAttributes.BLOCK_TYPE: vertex.block_type}
            for vertex in self.vertices
            if "alias" in vertex.attributes
        }

    def get_module_vertices_mapping(self) -> None:
        """
        For each vertex, if it's originated in a module import, add to the vertex the index of the
        matching module vertex as 'source_module'
        """
        for vertex in self.vertices:
            if not vertex.source_module_object:
                continue
            for idx in self.vertices_by_block_type[BlockType.MODULE]:
                if vertex.source_module_object.name != self.vertices[idx].name:
                    continue
                if vertex.source_module_object.path != self.vertices[idx].path:
                    continue
                if vertex.source_module_object.nested_tf_module != self.vertices[idx].source_module_object:
                    continue
                if vertex.source_module_object.foreach_idx != self.vertices[idx].for_each_index:
                    continue
                vertex.source_module.add(idx)
                break
        return

    def _build_edges(self) -> None:
        logging.info("Creating edges")
        self.get_module_vertices_mapping()
        aliases = self._get_aliases()
        resources_types = self.get_resources_types_in_graph()
        for origin_node_index, vertex in enumerate(self.vertices):
            self._build_edges_for_vertex(origin_node_index, vertex, aliases, resources_types)

    def _build_edges_for_vertex(self, origin_node_index: int, vertex: TerraformBlock, aliases: Dict[str, Dict[str, str]],
                                resources_types: List[str], cross_variable_edges: bool = False,
                                referenced_modules: Optional[List[Dict[str, Any]]] = None) -> None:

        attribute_is_leaf = get_attribute_is_leaf(vertex)
        for attribute_key, attribute_value in vertex.attributes.items():
            if attribute_key in reserved_attribute_names or attribute_has_nested_attributes(
                    attribute_key, vertex.attributes, attribute_is_leaf
            ):
                continue
            referenced_vertices = get_referenced_vertices_in_value(
                value=attribute_value,
                aliases=aliases,
                resources_types=resources_types,
            )
            for vertex_reference in referenced_vertices:
                # for certain blocks such as data and resource, the block name is composed from several parts.
                # the purpose of the loop is to avoid not finding the node if the name has several parts
                sub_values = [remove_index_pattern_from_str(sub_value) for sub_value in vertex_reference.sub_parts]
                for i in range(len(sub_values)):
                    reference_name = join_trimmed_strings(char_to_join=".", str_lst=sub_values, num_to_trim=i)
                    source_module_object = vertex.source_module_object
                    if referenced_modules is not None:
                        for module in referenced_modules:
                            referenced_module_idx = module.get("idx")
                            referenced_module_path = module.get("path")
                            if referenced_module_path is None:
                                dest_node_index = -1
                            else:
                                dest_node_index = self._find_vertex_index_relative_to_path(
                                    vertex_reference.block_type, reference_name, referenced_module_path,
                                    referenced_module_idx,
                                    source_module_object=source_module_object
                                )
                            self._create_edge_from_reference(attribute_key, origin_node_index, dest_node_index,
                                                             sub_values, vertex_reference, cross_variable_edges)
                    if vertex.source_module_object:
                        dest_node_index = self._find_vertex_index_relative_to_path(
                            vertex_reference.block_type, reference_name, vertex.path,
                            source_module_object=source_module_object
                        )
                        if dest_node_index == -1:
                            dest_node_index = self._find_vertex_index_relative_to_path(
                                vertex_reference.block_type, reference_name, vertex.path,
                                source_module_object=source_module_object
                            )
                    else:
                        dest_node_index = self._find_vertex_index_relative_to_path(
                            vertex_reference.block_type, reference_name, vertex.path,
                            source_module_object=source_module_object
                        )
                    if dest_node_index > -1 and origin_node_index > -1:
                        self._create_edge_from_reference(attribute_key, origin_node_index, dest_node_index, sub_values,
                                                         vertex_reference, cross_variable_edges)
                        break

        if vertex.block_type == BlockType.MODULE and vertex.attributes.get('source') \
                and isinstance(vertex.attributes['source'][0], str):
            dest_module_path = self._get_dest_module_path(
                curr_module_dir=self.get_dirname(vertex.path),
                dest_module_source=vertex.attributes["source"][0],
                dest_module_version=vertex.attributes.get("version", ["latest"])[0]
            )
            target_variables = self._get_target_variables(vertex, dest_module_path)
            for attribute in vertex.attributes.keys():
                if attribute in MODULE_RESERVED_ATTRIBUTES:
                    continue
                target_variable = next((v for v in target_variables if self.vertices[v].name == attribute), None)
                if target_variable is not None:
                    self.create_edge(target_variable, origin_node_index, "default", cross_variable_edges)
        elif vertex.block_type == BlockType.TF_VARIABLE:
            # Assuming the tfvars file is in the same directory as the variables file (best practice)
            target_variable = 0
            for index in self.vertices_block_name_map.get(BlockType.VARIABLE, {}).get(vertex.name, []):
                if self.get_dirname(self.vertices[index].path) == self.get_dirname(vertex.path):
                    target_variable = index
                    break
            if target_variable:
                self.create_edge(target_variable, origin_node_index, "default", cross_variable_edges)

    def _create_edge_from_reference(self, attribute_key: Any, origin_node_index: int, dest_node_index: int,
                                    sub_values: List[Any], vertex_reference: TerraformVertexReference,
                                    cross_variable_edges: bool) -> None:
        if dest_node_index > -1 and origin_node_index > -1:
            if vertex_reference.block_type == BlockType.MODULE:
                try:
                    self._connect_module(
                        sub_values, attribute_key, self.vertices[dest_node_index],
                        origin_node_index,
                        cross_variable_edges
                    )
                except Exception:
                    logging.warning(
                        f"Module {self.vertices[dest_node_index]} does not have source attribute, skipping"
                    )
            else:
                self.create_edge(origin_node_index, dest_node_index, attribute_key,
                                 cross_variable_edges)

    def _get_target_variables(self, vertex: TerraformBlock, dest_module_path: str) -> list[int]:
        target_path = get_vertex_as_tf_module(vertex)
        return [
            index
            for index in self.vertices_by_module_dependency.get(target_path, {}).get(BlockType.VARIABLE, [])
            if self.get_dirname(self.vertices[index].path) == dest_module_path
        ]

    def _build_cross_variable_edges(self) -> None:
        aliases = self._get_aliases()
        resources_types = self.get_resources_types_in_graph()
        for origin_node_index, referenced_vertices in self.out_edges.items():
            vertex = self.vertices[origin_node_index]
            if vertex.block_type == BlockType.RESOURCE and \
                    any(self.vertices[e.dest].block_type != BlockType.RESOURCE for e in referenced_vertices):
                modules = vertex.breadcrumbs.get(CustomAttributes.SOURCE_MODULE, [])
                self._build_edges_for_vertex(origin_node_index, vertex, aliases, resources_types, True, modules)

    def create_edge(self, origin_vertex_index: int, dest_vertex_index: int, label: str,
                    cross_variable_edges: bool = False) -> bool:
        if origin_vertex_index == dest_vertex_index:
            return False
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        if cross_variable_edges:
            if self.vertices[dest_vertex_index].block_type != BlockType.RESOURCE or \
                    self.vertices[origin_vertex_index].block_type != BlockType.RESOURCE:
                return False
            if edge in self.out_edges[origin_vertex_index]:
                return False
            edge.label = CROSS_VARIABLE_EDGE_PREFIX + edge.label
            if edge in self.out_edges[origin_vertex_index]:
                return False
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)
        return True

    def _connect_module(
        self, sub_values: List[str], attribute_key: str, module_node: TerraformBlock, origin_node_index: int, cross_variable_edges: bool = False
    ) -> None:
        """
        :param sub_values: list of sub values of the attribute value.
                            example: given 'instance_type = module.child.myoutput',
                                        then attribute_key = instance_type, sub_values = ['child', 'myoutput']
        :param attribute_key: the name of the attribute that has module block as value
        :param module_node: the graph node of the module

        The function receives a node of a block of type BlockType.Module, and finds all the nodes of blocks that belong to this
        module, and creates edges between them.
        """
        curr_module_dir = self.get_dirname(module_node.path)
        dest_module_source = module_node.attributes["source"][0]
        dest_module_version = module_node.attributes.get("version", ["latest"])[0]
        dest_module_path = self._get_dest_module_path(
            curr_module_dir=curr_module_dir,
            dest_module_source=dest_module_source,
            dest_module_version=dest_module_version
        )

        if len(sub_values) > 1:
            block_name_in_other_module = sub_values[1]
            output_blocks_with_name = self.vertices_block_name_map.get(BlockType.OUTPUT, {}).get(
                block_name_in_other_module, []
            )
            for vertex_index in output_blocks_with_name:
                vertex = self.vertices[vertex_index]
                if self._should_add_edge(vertex, dest_module_path, module_node):
                    added_edge = self.create_edge(origin_node_index, vertex_index, attribute_key, cross_variable_edges)
                    if added_edge:
                        self.vertices[origin_node_index].add_module_connection(attribute_key, vertex_index)
                    break

    def _get_dest_module_path(self, curr_module_dir: str, dest_module_source: str, dest_module_version: str) -> str:
        """
        :param curr_module_dir: current source directory
        :param dest_module_source: the value of module.source
        :return: the real path in the local file system of the dest module
        """
        relative_path_key = (curr_module_dir, dest_module_source)
        if relative_path_key in self.relative_paths_cache:
            return self.relative_paths_cache[relative_path_key]
        elif is_local_path(curr_module_dir, dest_module_source):
            self.relative_paths_cache[relative_path_key] = os.path.abspath(Path(curr_module_dir) / dest_module_source)
            return self.relative_paths_cache[relative_path_key]
        elif (dest_module_source, dest_module_version) in self.module.external_modules_source_map:
            return self.module.external_modules_source_map[(dest_module_source, dest_module_version)]

        # this happens, when we have external modules, which weren't downloaded
        return ""

    def _find_vertex_index_relative_to_path(
        self,
        block_type: str,
        name: str,
        block_path: str,
        relative_module_idx: Optional[int] = None,
        source_module_object: Optional[TFModule] = None,
    ) -> int:
        relative_vertices: list[int] = []
        if relative_module_idx is None:
            module_dependency_by_name_key = source_module_object
        else:
            vertex = self.vertices[relative_module_idx]
            module_dependency_by_name_key = vertex.source_module_object

        # important to use this specific map for big graph performance
        possible_vertices = self.vertices_by_module_dependency_by_name.get(module_dependency_by_name_key, {}).get(block_type, {}).get(name, [])
        for vertex_index in possible_vertices:
            vertex = self.vertices[vertex_index]
            if self.get_dirname(vertex.path) == self.get_dirname(block_path):
                relative_vertices.append(vertex_index)

        if len(relative_vertices) == 1:
            relative_vertex = relative_vertices[0]
        else:
            relative_vertex = self._find_vertex_with_longest_path_match(relative_vertices, block_path)
        return relative_vertex

    def _find_vertex_with_longest_path_match(self, relevant_vertices_indexes: List[int], origin_path: str) -> int:
        vertex_index_with_longest_common_prefix = -1
        longest_common_prefix = ""
        for vertex_index in relevant_vertices_indexes:
            vertex = self.vertices[vertex_index]
            common_prefix = os.path.commonpath([os.path.realpath(vertex.path), os.path.realpath(origin_path)])
            if len(common_prefix) > len(longest_common_prefix):
                vertex_index_with_longest_common_prefix = vertex_index
                longest_common_prefix = common_prefix
        return vertex_index_with_longest_common_prefix

    def get_vertices_hash_codes_to_attributes_map(self) -> Dict[str, Dict[str, Any]]:
        return {vertex.get_hash(): vertex.get_attribute_dict() for vertex in self.vertices}

    def order_edges_by_hash_codes(self) -> Dict[str, Edge]:
        edges = {}
        for edge in self.edges:
            edge_data = {
                "edge_label": edge.label,
                "from_vertex_hash": self.get_vertex_hash_by_index(vertex_index=edge.origin),
                "to_vertex_hash": self.get_vertex_hash_by_index(vertex_index=edge.dest),
            }
            edge_hash = calculate_hash(edge_data)
            edges[edge_hash] = edge
        return edges

    def get_vertex_hash_by_index(self, vertex_index: int) -> str:
        return self.vertex_hash_cache.setdefault(vertex_index, self.vertices[vertex_index].get_hash())

    def update_vertex_attribute(
        self,
        vertex_index: int,
        attribute_key: str,
        attribute_value: Any,
        change_origin_id: int | None,
        attribute_at_dest: Optional[Union[str, List[str]]],
        transform_step: bool = False,
    ) -> None:
        if change_origin_id is None:
            # no need to proceed further
            return

        previous_breadcrumbs = []
        attribute_at_dest = self.vertices[change_origin_id].find_attribute(attribute_at_dest)
        if attribute_at_dest:
            previous_breadcrumbs = self.vertices[change_origin_id].changed_attributes.get(attribute_at_dest, [])
        self.vertices[vertex_index].update_attribute(
            attribute_key, attribute_value, change_origin_id, previous_breadcrumbs, attribute_at_dest
        )

    def update_vertices_configs(self) -> None:
        for vertex in self.vertices:
            changed_attributes = list(vertex.changed_attributes.keys())
            changed_attributes = filter_sub_keys(changed_attributes)
            self.update_vertex_config(vertex, changed_attributes)

    @staticmethod
    def update_vertex_config(vertex: TerraformBlock, changed_attributes: Union[List[str], Dict[str, Any]], dynamic_blocks: bool = False) -> None:
        if not changed_attributes:
            # skip, if there is no change
            return

        vertex_name = vertex.name
        updated_config = pickle_deepcopy(vertex.config)
        if vertex.block_type == BlockType.PROVIDER:
            # provider blocks set the alias as a suffix to the name, ex. name: "aws.prod"
            vertex_name = vertex_name.split(".")[0]
        if vertex.block_type != BlockType.LOCALS:
            parts = vertex_name.split(".")
            start = 0
            end = 1
            while end <= len(parts):
                cur_key = ".".join(parts[start:end])
                if cur_key in updated_config:
                    updated_config = updated_config[cur_key]
                    start = end
                end += 1

        for changed_attribute in changed_attributes:
            new_value = vertex.attributes.get(changed_attribute, None)
            if new_value is not None:
                if vertex.block_type == BlockType.LOCALS:
                    changed_attribute = changed_attribute.replace(f"{vertex_name}.", "")
                updated_config = update_dictionary_attribute(updated_config, changed_attribute, new_value, dynamic_blocks)

        if len(changed_attributes) > 0:
            if vertex.block_type == BlockType.LOCALS:
                updated_local_config = updated_config.get(vertex_name)
                update_dictionary_attribute(vertex.config, vertex_name, updated_local_config, dynamic_blocks)
                return

            update_dictionary_attribute(vertex.config, vertex_name, updated_config, dynamic_blocks)

    def get_resources_types_in_graph(self) -> List[str]:
        return self.module.get_resources_types()

    def _update_vertices_breadcrumbs_and_module_connections(self) -> None:
        """
        The function processes each vertex's breadcrumbs:
        1. Get more data to each vertex in breadcrumb (name, path, hash and type)
        2. If a breadcrumb is originated in a different module, it will have 'module_connection'=True
        3. If a vertex has a 'source module' we will add a special breadcrumb for it
        """
        for vertex in self.vertices:
            for attribute_key, breadcrumbs_list in vertex.changed_attributes.items():
                hash_breadcrumbs = []
                for breadcrumb in breadcrumbs_list:
                    v = self.vertices[breadcrumb.vertex_id]
                    breadcrumb = v.get_export_data()
                    breadcrumb["module_connection"] = self._determine_if_module_connection(breadcrumbs_list, v)
                    hash_breadcrumbs.append(breadcrumb)
                vertex.breadcrumbs[attribute_key] = hash_breadcrumbs
            if len(vertex.source_module) == 1:
                v = vertex
                source_module_data = []
                while len(v.source_module) == 1:
                    idx = list(v.source_module)[0]
                    v = self.vertices[idx]
                    module_data = v.get_export_data()
                    module_data["idx"] = idx
                    if hasattr(vertex, "source_module_object"):
                        module_data["source_module_object"] = v.source_module_object
                    source_module_data.append(module_data)
                source_module_data.reverse()
                vertex.breadcrumbs[CustomAttributes.SOURCE_MODULE] = source_module_data

    @staticmethod
    def _determine_if_module_connection(breadcrumbs_list: List[int], vertex_in_breadcrumbs: TerraformBlock) -> bool:
        """
        :param breadcrumbs_list: list of vertex's breadcrumbs
        :param vertex_in_breadcrumbs: one of the vertices in the breadcrumb list
        :return: True if vertex_in_breadcrumbs has in its module_connections at least one of the vertices in breadcrumbs_list
        """
        if not vertex_in_breadcrumbs.module_connections:
            return False
        for connection_list in vertex_in_breadcrumbs.module_connections.values():
            if any(i in breadcrumbs_list for i in connection_list):
                return True
        return False

    def get_dirname(self, path: str) -> str:
        dir_name = self.dirname_cache.get(path)
        if not dir_name:
            dir_name = os.path.dirname(path)
            self.dirname_cache[path] = dir_name
        return dir_name

    def get_abspath(self, path: str) -> str:
        dir_name = self.abspath_cache.get(path)
        if not dir_name:
            dir_name = os.path.abspath(path)
            self.abspath_cache[path] = dir_name
        return dir_name

    def _update_nested_modules_address(self) -> None:
        for vertex in self.vertices:
            if vertex.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is not None:
                # Can happen for example in `tf_plan` files as the address already exists
                continue
            if vertex.block_type not in parser_registry.context_parsers:
                continue
            source_module = vertex.breadcrumbs.get(CustomAttributes.SOURCE_MODULE)

            address_prefix = ''
            if source_module:
                for module in source_module:
                    address_prefix += f"{module.get('type')}.{module.get('name')}."

            context_parser = parser_registry.context_parsers[vertex.block_type]
            entity_context_path = context_parser.get_entity_context_path(vertex.config)
            resource_id = '.'.join(entity_context_path) if entity_context_path else vertex.name
            address = f'{address_prefix}{resource_id}'
            vertex.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = address

            vertex_context = vertex.config
            definition_path = context_parser.get_entity_definition_path(vertex.config)
            for path in definition_path:
                vertex_context = vertex_context.get(path, vertex_context)
            vertex_context[CustomAttributes.TF_RESOURCE_ADDRESS] = address

    def _should_add_edge(self, vertex: TerraformBlock, dest_module_path: str, module_node: TerraformBlock) -> bool:
        if not vertex.source_module_object:
            return False

        return (self.get_dirname(vertex.path) == dest_module_path) and \
            (
                vertex.source_module_object == module_node.source_module_object  # The vertex is in the same file
                or self.get_abspath(vertex.source_module_object.path)
                == self.get_abspath(module_node.path)  # The vertex is in the correct dependency path)
        )


def to_list(data: Any) -> list[Any] | dict[str, Any]:
    if isinstance(data, list) and len(data) == 1 and (isinstance(data[0], str) or isinstance(data[0], int)):
        return data
    elif isinstance(data, list):
        return [to_list(x) for x in data]
    elif isinstance(data, dict):
        return {key: to_list(val) for key, val in data.items()}
    else:
        return [data]


@overload
def update_dictionary_attribute(
        config: dict[str, Any], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> dict[str, Any]:
    ...


@overload
def update_dictionary_attribute(
        config: list[Any], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> list[Any]:
    ...


def update_dictionary_attribute(
    config: Union[List[Any], Dict[str, Any]], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> Union[List[Any], Dict[str, Any]]:
    key_parts = key_to_update.split(".")
    if '"' in key_to_update:
        key_parts = join_double_quote_surrounded_dot_split(str_parts=key_parts)

    if isinstance(config, dict) and isinstance(key_parts, list):
        key = key_parts[0]
        inner_config = config.get(key)

        if inner_config is not None:
            if len(key_parts) == 1:
                if isinstance(inner_config, list) and not isinstance(new_value, list):
                    new_value = [new_value]
                config[key] = to_list(new_value) if dynamic_blocks else new_value
                return config
            else:
                config[key] = update_dictionary_attribute(
                    inner_config, ".".join(key_parts[1:]), new_value, dynamic_blocks=dynamic_blocks
                )
        else:
            for key in config:
                config[key] = update_dictionary_attribute(
                    config[key], key_to_update, new_value, dynamic_blocks=dynamic_blocks
                )
    if isinstance(config, list):
        return update_list_attribute(
            config=config,
            key_parts=key_parts,
            key_to_update=key_to_update,
            new_value=new_value,
            dynamic_blocks=dynamic_blocks,
        )
    return config


def update_list_attribute(
    config: list[Any], key_parts: list[str], key_to_update: str, new_value: Any, dynamic_blocks: bool = False
) -> list[Any] | dict[str, Any]:
    """Updates a list attribute in the given config"""

    if not config:
        # happens when we can't correctly evaluate something, because of strange defaults or 'for_each' blocks
        return config

    if len(key_parts) == 1:
        idx = force_int(key_parts[0])
        inner_config = config[0]

        if idx is not None and isinstance(inner_config, list):
            if not inner_config:
                # happens when config = [[]]
                return config

            inner_config[idx] = new_value
            return config
    entry_to_update = int(key_parts[0]) if key_parts[0].isnumeric() else -1
    for i, config_value in enumerate(config):
        if entry_to_update == -1:
            config[i] = update_dictionary_attribute(config=config_value, key_to_update=key_to_update, new_value=new_value, dynamic_blocks=dynamic_blocks)
        elif entry_to_update == i:
            config[i] = update_dictionary_attribute(config=config_value, key_to_update=".".join(key_parts[1:]), new_value=new_value, dynamic_blocks=dynamic_blocks)

    return config


def get_vertex_as_tf_module(block: TerraformBlock) -> TFModule:
    return TFModule(block.path, block.name, block.source_module_object)
