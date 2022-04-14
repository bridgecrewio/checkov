import logging
import os
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import List, Optional, Union, Any, Dict, Set, Tuple

from typing_extensions import TypedDict

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder import reserved_attribute_names
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.graph.graph_builder.utils import calculate_hash, join_trimmed_strings
from checkov.terraform.checks.utils.dependency_path_handler import unify_dependency_path
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE
from checkov.terraform.graph_builder.graph_components.module import Module
from checkov.terraform.graph_builder.utils import (
    get_referenced_vertices_in_value,
    filter_sub_keys,
    attribute_has_nested_attributes, remove_index_pattern_from_str,
)
from checkov.terraform.graph_builder.utils import is_local_path
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer

MODULE_RESERVED_ATTRIBUTES = ("source", "version")


class Undetermined(TypedDict):
    module_vertex_id: int
    attribute_name: str
    variable_vertex_id: int


class TerraformLocalGraph(LocalGraph):
    def __init__(self, module: Module) -> None:
        super().__init__()
        self.module = module
        self.map_path_to_module: Dict[str, List[int]] = {}
        self.relative_paths_cache = {}
        self.abspath_cache: Dict[str, str] = {}
        self.dirname_cache: Dict[str, str] = {}
        self.vertices_by_module_dependency_by_name: Dict[Tuple[str, str], Dict[BlockType, Dict[str, List[int]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.vertices_by_module_dependency: Dict[Tuple[str, str], Dict[BlockType, List[int]]] = defaultdict(lambda: defaultdict(list))

    def build_graph(self, render_variables: bool) -> None:
        self._create_vertices()
        self._build_edges()
        self.calculate_encryption_attribute(ENCRYPTION_BY_RESOURCE_TYPE)
        if render_variables:
            logging.info(f"Rendering variables, graph has {len(self.vertices)} vertices and {len(self.edges)} edges")
            renderer = TerraformVariableRenderer(self)
            renderer.render_variables_from_local_graph()
            self.update_vertices_breadcrumbs_and_module_connections()

    def _create_vertices(self) -> None:
        logging.info("Creating vertices")
        self.vertices: List[TerraformBlock] = [None] * len(self.module.blocks)  # type: ignore
        for i, block in enumerate(self.module.blocks):
            self.vertices[i] = block

            self.vertices_by_block_type[block.block_type].append(i)
            self.vertices_block_name_map[block.block_type][block.name].append(i)

            if block.block_type == BlockType.MODULE:
                # map between file paths and module vertices indexes from that file
                self.map_path_to_module.setdefault(block.path, []).append(i)

            self.vertices_by_module_dependency[(block.module_dependency, block.module_dependency_num)][block.block_type].append(i)
            self.vertices_by_module_dependency_by_name[(block.module_dependency, block.module_dependency_num)][block.block_type][block.name].append(i)

            self.in_edges[i] = []
            self.out_edges[i] = []

    def _set_variables_values_from_modules(self) -> List[Undetermined]:
        undetermined_values: List[Undetermined] = []
        for module_vertex_id in self.vertices_by_block_type.get(BlockType.MODULE, []):
            module_vertex = self.vertices[module_vertex_id]
            for attribute_name, attribute_value in module_vertex.attributes.items():
                matching_variables = self.vertices_block_name_map.get(BlockType.VARIABLE, {}).get(attribute_name, [])
                for variable_vertex_id in matching_variables:
                    variable_dir = os.path.dirname(self.vertices[variable_vertex_id].path)
                    # TODO: module_vertex.path is always a string and the retrieved dict value is a nested list
                    #   therefore this condition is always false. Fixing it results in some variables not being rendered.
                    #   see test: tests.graph.terraform.variable_rendering.test_render_scenario.TestRendererScenarios.test_account_dirs_and_modules
                    if module_vertex.path in self.module.module_dependency_map.get(variable_dir, []):
                        has_var_reference = get_referenced_vertices_in_value(
                            value=attribute_value, aliases={}, resources_types=self.get_resources_types_in_graph()
                        )
                        if has_var_reference:
                            undetermined_values.append(
                                {
                                    "module_vertex_id": module_vertex_id,
                                    "attribute_name": attribute_name,
                                    "variable_vertex_id": variable_vertex_id,
                                }
                            )
                        var_default_value = self.vertices[variable_vertex_id].attributes.get("default")
                        if (
                            not has_var_reference
                            or not var_default_value
                            or get_referenced_vertices_in_value(
                                value=var_default_value, aliases={}, resources_types=self.get_resources_types_in_graph()
                            )
                        ):
                            self.update_vertex_attribute(
                                variable_vertex_id, "default", attribute_value, module_vertex_id, attribute_name
                            )
        return undetermined_values

    def _get_aliases(self) -> Dict[str, Dict[str, BlockType]]:
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
        block_dirs_to_modules: Dict[Tuple[str, str], Dict[str, Set[int]]] = defaultdict(dict)
        for dir_name, paths_to_modules in self.module.module_dependency_map.items():
            # for each directory, find the module vertex that imported it
            for path_to_module in paths_to_modules:
                if not path_to_module:
                    continue
                path_to_module_str = unify_dependency_path(path_to_module)
                if block_dirs_to_modules.get((dir_name, path_to_module_str)):
                    continue
                module_list = self.map_path_to_module.get(path_to_module[-1], [])
                for module_index in module_list:
                    module_vertex = self.vertices[module_index]
                    if module_vertex.module_dependency == unify_dependency_path(path_to_module[:-1]):
                        module_vertex_dir = self.get_dirname(module_vertex.path)
                        module_source = module_vertex.attributes.get("source", [""])[0]
                        module_version = module_vertex.attributes.get("version", ["latest"])[0]
                        dest_module_path = self._get_dest_module_path(
                            curr_module_dir=module_vertex_dir,
                            dest_module_source=module_source,
                            dest_module_version=module_version
                        )
                        if dest_module_path == dir_name:
                            module_dependency_num = self.module.module_address_map.get((module_vertex.path, module_vertex.name))
                            if module_dependency_num:
                                block_dirs_to_modules[(dir_name, path_to_module_str)].setdefault(module_dependency_num, set()).add(module_index)

        for vertex in self.vertices:
            # match the right module vertex according to the vertex path directory
            module_dependency_nums = block_dirs_to_modules.get((self.get_dirname(vertex.path), vertex.module_dependency))
            if module_dependency_nums:
                module_indices = module_dependency_nums.get(vertex.module_dependency_num)
                if module_indices:
                    vertex.source_module = module_indices

    def _build_edges(self) -> None:
        logging.info("Creating edges")
        self.get_module_vertices_mapping()
        aliases = self._get_aliases()
        for origin_node_index, vertex in enumerate(self.vertices):
            for attribute_key in vertex.attributes:
                if attribute_key in reserved_attribute_names or attribute_has_nested_attributes(
                    attribute_key, vertex.attributes
                ):
                    continue
                referenced_vertices = get_referenced_vertices_in_value(
                    value=vertex.attributes[attribute_key],
                    aliases=aliases,
                    resources_types=self.get_resources_types_in_graph(),
                )
                for vertex_reference in referenced_vertices:
                    # for certain blocks such as data and resource, the block name is composed from several parts.
                    # the purpose of the loop is to avoid not finding the node if the name has several parts
                    sub_values = [remove_index_pattern_from_str(sub_value) for sub_value in vertex_reference.sub_parts]
                    for i, _ in enumerate(sub_values):
                        reference_name = join_trimmed_strings(char_to_join=".", str_lst=sub_values, num_to_trim=i)
                        if vertex.module_dependency:
                            dest_node_index = self._find_vertex_index_relative_to_path(
                                vertex_reference.block_type, reference_name, vertex.path, vertex.module_dependency, vertex.module_dependency_num
                            )
                            if dest_node_index == -1:
                                dest_node_index = self._find_vertex_index_relative_to_path(
                                    vertex_reference.block_type, reference_name, vertex.path, vertex.path, vertex.module_dependency_num
                                )
                        else:
                            dest_node_index = self._find_vertex_index_relative_to_path(
                                vertex_reference.block_type, reference_name, vertex.path, vertex.module_dependency, vertex.module_dependency_num
                            )
                        if dest_node_index > -1 and origin_node_index > -1:
                            if vertex_reference.block_type == BlockType.MODULE:
                                try:
                                    self._connect_module(
                                        sub_values, attribute_key, self.vertices[dest_node_index], origin_node_index
                                    )
                                except Exception as e:
                                    logging.warning(
                                        f"Module {self.vertices[dest_node_index]} does not have source attribute, skipping"
                                    )
                                    logging.warning(e, stack_info=True)
                            else:
                                self._create_edge(origin_node_index, dest_node_index, attribute_key)
                            break

            if vertex.block_type == BlockType.MODULE and vertex.attributes.get('source'):
                target_path = vertex.path
                if vertex.module_dependency != "":
                    target_path = unify_dependency_path([vertex.module_dependency, vertex.path])
                dest_module_path = self._get_dest_module_path(
                    curr_module_dir=self.get_dirname(vertex.path),
                    dest_module_source=vertex.attributes["source"][0],
                    dest_module_version=vertex.attributes.get("version", ["latest"])[0]
                )
                target_variables = [
                    index
                    for index in self.vertices_by_module_dependency.get((target_path, self.module.module_address_map.get((vertex.path, vertex.name))), {}).get(BlockType.VARIABLE, [])
                    if self.get_dirname(self.vertices[index].path) == dest_module_path
                ]
                for attribute, value in vertex.attributes.items():
                    if attribute in MODULE_RESERVED_ATTRIBUTES:
                        continue
                    target_variable = next((v for v in target_variables if self.vertices[v].name == attribute), None)
                    if target_variable is not None:
                        self._create_edge(target_variable, origin_node_index, "default")
            elif vertex.block_type == BlockType.TF_VARIABLE:
                # Assuming the tfvars file is in the same directory as the variables file (best practice)
                target_variables = [
                    index
                    for index in self.vertices_block_name_map.get(BlockType.VARIABLE, {}).get(vertex.name, [])
                    if self.get_dirname(self.vertices[index].path) == self.get_dirname(vertex.path)
                ]
                if len(target_variables) == 1:
                    self._create_edge(target_variables[0], origin_node_index, "default")

    def _create_edge(self, origin_vertex_index: int, dest_vertex_index: int, label: str) -> None:
        if origin_vertex_index == dest_vertex_index:
            return
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)

    def _connect_module(
        self, sub_values: List[str], attribute_key: str, module_node: TerraformBlock, origin_node_index: int
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
                if (self.get_dirname(vertex.path) == dest_module_path) and (
                    vertex.module_dependency == module_node.module_dependency  # The vertex is in the same file
                    or self.get_abspath(vertex.module_dependency)
                    == self.get_abspath(module_node.path)  # The vertex is in the correct dependency path
                ):
                    self._create_edge(origin_node_index, vertex_index, attribute_key)
                    self.vertices[origin_node_index].add_module_connection(attribute_key, vertex_index)
                    break

    def _get_dest_module_path(self, curr_module_dir: str, dest_module_source: str, dest_module_version: str) -> str:
        """
        :param curr_module_dir: current source directory
        :param dest_module_source: the value of module.source
        :return: the real path in the local file system of the dest module
        """
        dest_module_path = Path()
        if is_local_path(curr_module_dir, dest_module_source):
            dest_module_path = Path(curr_module_dir) / dest_module_source
        elif (dest_module_source, dest_module_version) in self.module.external_modules_source_map:
            return self.module.external_modules_source_map[(dest_module_source, dest_module_version)]
        else:
            try:
                if dest_module_source not in self.relative_paths_cache:
                    self.relative_paths_cache[dest_module_source] = list(Path(self.module.source_dir).rglob(dest_module_source))
                dest_module_path = next(
                    (path for path in self.relative_paths_cache.get(dest_module_source)), dest_module_path
                )
            except NotImplementedError as e:
                if 'Non-relative patterns are unsupported' in str(e):
                    return ""
                raise e
        return os.path.realpath(dest_module_path)

    def _find_vertex_index_relative_to_path(
        self, block_type: BlockType, name: str, block_path: str, module_path: str, module_num: str
    ) -> int:
        relative_vertices = []
        possible_vertices = self.vertices_by_module_dependency_by_name.get((module_path, module_num), {}).get(block_type, {}).get(name, [])
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
        change_origin_id: int,
        attribute_at_dest: Optional[Union[str, List[str]]],
    ) -> None:
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

    def update_vertex_config(self, vertex: TerraformBlock, changed_attributes: Union[List[str], Dict[str, Any]]) -> None:
        if not changed_attributes:
            # skip, if there is no change
            return

        updated_config = deepcopy(vertex.config)
        if vertex.block_type != BlockType.LOCALS:
            parts = vertex.name.split(".")
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
                    changed_attribute = changed_attribute.replace(vertex.name + ".", "")
                updated_config = update_dictionary_attribute(updated_config, changed_attribute, new_value)

        if len(changed_attributes) > 0:
            if vertex.block_type == BlockType.LOCALS:
                updated_config = updated_config.get(vertex.name)
            update_dictionary_attribute(vertex.config, vertex.name, updated_config)

    def get_resources_types_in_graph(self) -> List[str]:
        return self.module.get_resources_types()

    def update_vertices_breadcrumbs_and_module_connections(self) -> None:
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
                m = self.vertices[list(vertex.source_module)[0]]
                source_module_data = [m.get_export_data()]
                while len(m.source_module) == 1:
                    m = self.vertices[list(m.source_module)[0]]
                    source_module_data.append(m.get_export_data())
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


def update_dictionary_attribute(
        config: Union[List[Any], Dict[str, Any]], key_to_update: str, new_value: Any
) -> Union[List[Any], Dict[str, Any]]:
    key_parts = key_to_update.split(".")
    if isinstance(config, dict):
        if config.get(key_parts[0]) is not None:
            key = key_parts[0]
            if len(key_parts) == 1:
                if isinstance(config[key], list) and not isinstance(new_value, list):
                    new_value = [new_value]
                config[key] = new_value
                return config
            else:
                config[key] = update_dictionary_attribute(config[key], ".".join(key_parts[1:]), new_value)
        else:
            for key in config:
                config[key] = update_dictionary_attribute(config[key], key_to_update, new_value)
    if isinstance(config, list):
        for i, config_value in enumerate(config):
            config[i] = update_dictionary_attribute(config_value, key_to_update, new_value)

    return config
