import logging
import os
from copy import deepcopy
from typing import List, Optional, Union

from checkov.common.graph.graph_builder import reserved_attribute_names, EncryptionValues
from checkov.common.graph.graph_builder import Edge
from checkov.terraform.checks.utils.dependency_path_handler import unify_dependency_path
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.generic_resource_encryption import \
    ENCRYPTION_BY_RESOURCE_TYPE
from checkov.terraform.graph_builder.utils import is_local_path
from checkov.terraform.checks.utils.utils import get_referenced_vertices_in_value, update_dictionary_attribute, \
    join_trimmed_strings, filter_sub_keys, attribute_has_nested_attributes
from checkov.terraform.checks.utils.utils import remove_index_pattern_from_str, calculate_hash
from checkov.terraform.variable_rendering.renderer import VariableRenderer

MODULE_RESERVED_ATTRIBUTES = ('source', 'version')


class LocalGraph:
    def __init__(self, module, module_dependency_map):
        self.module = module
        self.vertices = []
        self.edges = []
        self.in_edges = {}  # map between vertex index and the edges entering it
        self.out_edges = {}  # map between vertex index and the edges exiting it
        self.vertices_by_block_type = {}
        self.vertex_hash_cache = {}
        self.vertices_block_name_map = {}
        self.module_dependency_map = module_dependency_map
        self.map_path_to_module = {}
        self.relative_paths_cache = {}

    def build_graph(self, render_variables):
        self._create_vertices()
        undetermined_values = self._set_variables_values_from_modules()
        self._build_edges()
        self.calculate_encryption_attribute()
        if render_variables:
            logging.info('Rendering variables')
            renderer = VariableRenderer(self)
            renderer.render_variables_from_local_graph()
            self.update_vertices_breadcrumbs_and_module_connections()
            self.process_undetermined_values(undetermined_values)

    def _create_vertices(self):
        logging.info('Creating vertices')
        self.vertices = [None] * len(self.module.blocks)
        for i, block in enumerate(self.module.blocks):
            self.vertices[i] = block

            if not self.vertices_by_block_type.get(block.block_type):
                self.vertices_by_block_type[block.block_type] = []
            self.vertices_by_block_type[block.block_type].append(i)

            if block.block_type not in self.vertices_block_name_map:
                self.vertices_block_name_map[block.block_type] = {}
            if block.name not in self.vertices_block_name_map[block.block_type]:
                self.vertices_block_name_map[block.block_type][block.name] = []
            self.vertices_block_name_map[block.block_type][block.name].append(i)

            if block.block_type == BlockType.MODULE:
                # map between file paths and module vertices indexes from that file
                if not self.map_path_to_module.get(block.path):
                    self.map_path_to_module[block.path] = []
                self.map_path_to_module[block.path].append(i)

            self.in_edges[i] = []
            self.out_edges[i] = []

    def _set_variables_values_from_modules(self):
        undetermined_values = []
        for module_vertex_id in self.vertices_by_block_type.get(BlockType.MODULE, []):
            module_vertex = self.vertices[module_vertex_id]
            for attribute_name in module_vertex.attributes:
                matching_variables = self.vertices_block_name_map.get(BlockType.VARIABLE, {}).get(attribute_name, [])
                for variable_vertex_id in matching_variables:
                    variable_vertex = self.vertices[variable_vertex_id]
                    variable_dir = os.path.dirname(variable_vertex.path)
                    if module_vertex.path in self.module_dependency_map.get(variable_dir, []):
                        attribute_value = module_vertex.attributes[attribute_name]
                        has_var_reference = get_referenced_vertices_in_value(value=attribute_value, aliases={},
                                                            resources_types=self.get_resources_types_in_graph())
                        if has_var_reference:
                            undetermined_values.append(
                                {'module_vertex_id': module_vertex_id, 'attribute_name': attribute_name,
                                 'variable_vertex_id': variable_vertex_id})
                        var_default_value = self.vertices[variable_vertex_id].attributes.get("default")
                        if not has_var_reference or not var_default_value or get_referenced_vertices_in_value(value=var_default_value, aliases={},
                                                            resources_types=self.get_resources_types_in_graph()):
                            self.update_vertex_attribute(variable_vertex_id, 'default', attribute_value,
                                                         module_vertex_id, attribute_name)
        return undetermined_values

    def process_undetermined_values(self, undetermined_values):
        for undetermined in undetermined_values:
            module_vertex = self.vertices[undetermined.get('module_vertex_id')]
            value = module_vertex.attributes.get(undetermined.get('attribute_name'))
            if not get_referenced_vertices_in_value(value=value, aliases={},
                                                    resources_types=self.get_resources_types_in_graph()):
                self.update_vertex_attribute(undetermined.get('variable_vertex_id'), 'default', value,
                                             undetermined.get('module_vertex_id'), undetermined.get('attribute_name'))

    def _get_aliases(self):
        """
        :return aliases: map between alias names that are found inside the blocks and the block type their aliased to.
        """
        aliases = {}
        for vertex in self.vertices:
            if 'alias' in vertex.attributes:
                aliases[vertex.name] = {CustomAttributes.BLOCK_TYPE: vertex.block_type}
        return aliases

    def get_module_vertices_mapping(self):
        """
        For each vertex, if it's originated in a module import, add to the vertex the index of the
        matching module vertex as 'source_module'
        """
        block_dirs_to_modules = {}
        for dir_name, paths_to_modules in self.module_dependency_map.items():
            # for each directory, find the module vertex that imported it
            if block_dirs_to_modules.get(dir_name):
                continue
            for path_to_module in paths_to_modules:
                if not path_to_module:
                    continue
                path_to_module = unify_dependency_path(path_to_module)
                module_list = self.map_path_to_module.get(path_to_module, [])
                for module_index in module_list:
                    module_vertex = self.vertices[module_index]
                    module_vertex_dir = os.path.dirname(module_vertex.path)
                    module_source = self.vertices[module_index].attributes.get('source', [''])[0]
                    if self._get_dest_module_path(module_vertex_dir, module_source) == dir_name:
                        if not block_dirs_to_modules.get(dir_name):
                            block_dirs_to_modules[dir_name] = set()
                        block_dirs_to_modules[dir_name].add(module_index)

        for vertex in self.vertices:
            # match the right module vertex according to the vertex path directory
            module_index = block_dirs_to_modules.get(os.path.dirname(vertex.path), set())
            if module_index:
                vertex.source_module = module_index

    def _build_edges(self):
        logging.info('Creating edges')
        self.get_module_vertices_mapping()
        aliases = self._get_aliases()
        for origin_node_index, vertex in enumerate(self.vertices):
            for attribute_key in vertex.attributes:
                if attribute_key in reserved_attribute_names or attribute_has_nested_attributes(attribute_key,
                                                                                                     vertex.attributes):
                    continue
                referenced_vertices = get_referenced_vertices_in_value(value=vertex.attributes[attribute_key],
                                                                       aliases=aliases,
                                                                       resources_types=self.get_resources_types_in_graph())
                for vertex_reference in referenced_vertices:
                    # for certain blocks such as data and resource, the block name is composed from several parts.
                    # the purpose of the loop is to avoid not finding the node if the name has several parts
                    sub_values = [remove_index_pattern_from_str(sub_value) for sub_value in vertex_reference.sub_parts]
                    for i in range(len(sub_values)):
                        reference_name = join_trimmed_strings(char_to_join=".", str_lst=sub_values, num_to_trim=i)
                        if vertex.module_dependency:
                            dest_node_index = self._find_vertex_index_relative_to_path(vertex_reference.block_type,
                                                                                       reference_name,
                                                                                       vertex.path,
                                                                                       vertex.module_dependency)
                            if dest_node_index == -1:
                                dest_node_index = self._find_vertex_index_relative_to_path(vertex_reference.block_type,
                                                                                           reference_name,
                                                                                           vertex.path,
                                                                                           vertex.path)
                        else:
                            dest_node_index = self._find_vertex_index_relative_to_path(vertex_reference.block_type,
                                                                                       reference_name,
                                                                                       vertex.path,
                                                                                       vertex.module_dependency)
                        if dest_node_index > -1 and origin_node_index > -1:
                            if vertex_reference.block_type == BlockType.MODULE:
                                try:
                                    self._connect_module(sub_values, attribute_key, self.vertices[dest_node_index],
                                                         origin_node_index)
                                except Exception as e:
                                    logging.warning(
                                        f'Module {self.vertices[dest_node_index]} does not have source attribute, skipping')
                                    logging.warning(e, stack_info=True)
                            else:
                                self._create_edge(origin_node_index, dest_node_index, attribute_key)
                            break

            if vertex.block_type == BlockType.MODULE:
                target_path = vertex.path
                if vertex.module_dependency != '':
                    target_path = unify_dependency_path([vertex.module_dependency, vertex.path])
                target_variables = list(filter(lambda v: self.vertices[v].module_dependency == target_path,
                                               self.vertices_by_block_type.get(BlockType.VARIABLE, {})))
                for attribute, value in vertex.attributes.items():
                    if attribute in MODULE_RESERVED_ATTRIBUTES:
                        continue
                    target_variable = None
                    for v in target_variables:
                        if self.vertices[v].name == attribute:
                            target_variable = v
                            break
                    if target_variable is not None:
                        self._create_edge(target_variable, origin_node_index, 'default')
            elif vertex.block_type == BlockType.TF_VARIABLE:
                if vertex.module_dependency != '':
                    target_path = unify_dependency_path([vertex.module_dependency, vertex.path])
                # Assuming the tfvars file is in the same directory as the variables file (best practice)
                target_variables = list(filter(lambda v: os.path.dirname(self.vertices[v].path) == os.path.dirname(vertex.path),
                                               self.vertices_block_name_map.get(BlockType.VARIABLE, {}).get(vertex.name, [])))
                if len(target_variables) == 1:
                    self._create_edge(target_variables[0], origin_node_index, 'default')


    def _create_edge(self, origin_vertex_index, dest_vertex_index, label):
        if origin_vertex_index == dest_vertex_index:
            return
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)

    def _connect_module(self, sub_values, attribute_key, module_node, origin_node_index):
        """
        :param sub_values: list of sub values of the attribute value.
                            example: given 'instance_type = module.child.myoutput',
                                        then attribute_key = instance_type, sub_values = ['child', 'myoutput']
        :param attribute_key: the name of the attribute that has module block as value
        :param module_node: the graph node of the module

        The function receives a node of a block of type BlockType.Module, and finds all the nodes of blocks that belong to this
        module, and creates edges between them.
        """
        curr_module_dir = os.path.dirname(module_node.path)
        dest_module_source = module_node.attributes['source'][0]
        dest_module_path = self._get_dest_module_path(curr_module_dir, dest_module_source)

        if len(sub_values) > 1:
            block_name_in_other_module = sub_values[1]
            output_blocks_with_name = self.vertices_block_name_map.get(BlockType.OUTPUT, {}).get(
                block_name_in_other_module, [])
            for vertex_index in output_blocks_with_name:
                vertex = self.vertices[vertex_index]
                if os.path.dirname(vertex.path) == dest_module_path and \
                        (vertex.module_dependency == module_node.module_dependency or # The vertex is in the same file
                         os.path.abspath(vertex.module_dependency) == os.path.abspath(module_node.path)): # The vertex is in the correct dependency path
                    self._create_edge(origin_node_index, vertex_index, attribute_key)
                    self.vertices[origin_node_index].add_module_connection(attribute_key, vertex_index)
                    break

    def _get_dest_module_path(self, curr_module_dir, dest_module_source):
        """
        :param curr_module_dir: current source directory
        :param dest_module_source: the value of module.source
        :return: the real path in the local file system of the dest module
        """
        dest_module_path = ''
        if is_local_path(curr_module_dir, dest_module_source):
            dest_module_path = os.path.join(curr_module_dir, dest_module_source)
        else:
            for root, d_names, f_names in os.walk(self.module.source_dir):
                dest_module_path = os.path.join(root, dest_module_source)
                if os.path.exists(dest_module_path):
                    break
        return os.path.realpath(dest_module_path)

    def _find_vertex_index_relative_to_path(self, block_type, name, block_path, module_path):
        relative_vertices = []
        possible_vertices = self.vertices_block_name_map.get(block_type, {}).get(name, [])
        for vertex_index in possible_vertices:
            vertex = self.vertices[vertex_index]
            if vertex.module_dependency == module_path and os.path.dirname(vertex.path) == os.path.dirname(block_path):
                relative_vertices.append(vertex_index)

        if len(relative_vertices) == 1:
            return relative_vertices[0]
        return self._find_vertex_with_longest_path_match(relative_vertices, block_path)

    def _find_vertex_with_longest_path_match(self, relevant_vertices_indexes, origin_path) -> int:
        vertex_index_with_longest_common_prefix = -1
        longest_common_prefix = ''
        for vertex_index in relevant_vertices_indexes:
            vertex = self.vertices[vertex_index]
            common_prefix = os.path.commonpath([os.path.realpath(vertex.path), os.path.realpath(origin_path)])
            if len(common_prefix) > len(longest_common_prefix):
                vertex_index_with_longest_common_prefix = vertex_index
                longest_common_prefix = common_prefix
        return vertex_index_with_longest_common_prefix

    def get_vertices_hash_codes_to_attributes_map(self):
        return {vertex.get_hash(): vertex.get_decoded_attribute_dict() for vertex in self.vertices}

    def order_edges_by_hash_codes(self):
        edges = {}
        for edge in self.edges:
            edge_data = {'edge_label': edge.label,
                         'from_vertex_hash': self.get_vertex_hash_by_index(vertex_index=edge.origin),
                         'to_vertex_hash': self.get_vertex_hash_by_index(vertex_index=edge.dest),
                         }
            edge_hash = calculate_hash(edge_data)
            edges[edge_hash] = edge
        return edges

    def get_vertex_attributes_by_index(self, index):
        return self.vertices[index].get_decoded_attribute_dict()

    def get_vertices_with_degrees_conditions(self, out_degree_cond, in_degree_cond):
        vertices_with_out_degree = set([vertex_index for vertex_index in self.out_edges.keys() if
                                        out_degree_cond(len(self.out_edges.get(vertex_index)))])
        vertices_with_in_degree = set([vertex_index for vertex_index in self.in_edges.keys() if
                                       in_degree_cond(len(self.in_edges.get(vertex_index)))])

        return list(vertices_with_in_degree.intersection(vertices_with_out_degree))

    def get_vertex_hash_by_index(self, vertex_index):
        if vertex_index not in self.vertex_hash_cache:
            self.vertex_hash_cache[vertex_index] = self.vertices[vertex_index].get_hash()
        return self.vertex_hash_cache[vertex_index]

    def get_in_edges(self, end_vertices):
        res = []
        for vertex in end_vertices:
            res.extend(self.in_edges.get(vertex, []))
        return self.sort_edged_by_dest_out_degree(res)

    def sort_edged_by_dest_out_degree(self, edges):
        edged_by_out_degree = {}
        for edge in edges:
            dest_out_degree = len(self.out_edges.get(edge.dest))
            if not edged_by_out_degree.get(dest_out_degree):
                edged_by_out_degree[dest_out_degree] = []
            edged_by_out_degree[dest_out_degree].append(edge)
        sorted_edges = []
        for degree in sorted(edged_by_out_degree.keys()):
            sorted_edges.extend(edged_by_out_degree[degree])
        return sorted_edges

    def update_vertex_attribute(
            self,
            vertex_index: int,
            attribute_key: str,
            attribute_value: List[str],
            change_origin_id: int,
            attribute_at_dest: Optional[Union[str, List[str]]]
    ) -> None:
        previous_breadcrumbs = []
        attribute_at_dest = self.vertices[change_origin_id].find_attribute(attribute_at_dest)
        if attribute_at_dest:
            previous_breadcrumbs = self.vertices[change_origin_id].changed_attributes.get(attribute_at_dest, [])
        self.vertices[vertex_index].update_attribute(attribute_key, attribute_value, change_origin_id,
                                                     previous_breadcrumbs)

    def update_vertices_configs(self):
        for vertex in self.vertices:
            changed_attributes = list(vertex.changed_attributes.keys())
            changed_attributes = filter_sub_keys(changed_attributes)
            self.update_vertex_config(vertex, changed_attributes)

    @staticmethod
    def update_vertex_config(vertex, changed_attributes):
        updated_config = deepcopy(vertex.config)
        if vertex.block_type != BlockType.LOCALS:
            parts = vertex.name.split('.')
            start = 0
            end = 1
            while end <= len(parts):
                cur_key = '.'.join(parts[start:end])
                if cur_key in updated_config:
                    updated_config = updated_config[cur_key]
                    start = end
                end += 1
        for changed_attribute in changed_attributes:
            new_value = vertex.attributes.get(changed_attribute, None)
            if new_value is not None:
                if vertex.block_type == BlockType.LOCALS:
                    changed_attribute = changed_attribute.replace(vertex.name + ".", '')
                updated_config = update_dictionary_attribute(updated_config, changed_attribute, new_value)

        if len(changed_attributes) > 0:
            if vertex.block_type == BlockType.LOCALS:
                updated_config = updated_config.get(vertex.name)
            update_dictionary_attribute(vertex.config, vertex.name, updated_config)

    def get_resources_types_in_graph(self):
        return self.module.get_resources_types()

    def update_vertices_breadcrumbs_and_module_connections(self):
        """
        The function processes each vertex's breadcrumbs:
        1. Get more data to each vertex in breadcrumb (name, path, hash and type)
        2. If a breadcrumb is originated in a different module, it will have 'module_connection'=True
        3. If a vertex has a 'source module' we will add a special breadcrumb for it
        """
        for vertex in self.vertices:
            for attribute_key, breadcrumbs_list in vertex.changed_attributes.items():
                hash_breadcrumbs = []
                for vertex_id in breadcrumbs_list:
                    v = self.vertices[vertex_id]
                    breadcrumb = v.get_export_data()
                    breadcrumb['module_connection'] = self._determine_if_module_connection(breadcrumbs_list, v)
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
    def _determine_if_module_connection(breadcrumbs_list, vertex_in_breadcrumbs):
        """
        :param breadcrumbs_list: list of vertex's breadcrumbs
        :param vertex_in_breadcrumbs: one of the vertices in the breadcrumb list
        :return: True if vertex_in_breadcrumbs has in its module_connections at least one of the vertices in breadcrumbs_list
        """
        if not vertex_in_breadcrumbs.module_connections:
            return False
        for connection_list in vertex_in_breadcrumbs.module_connections.values():
            same_ids = [i for i in connection_list if i in breadcrumbs_list]
            if len(same_ids) > 0:
                return True
        return False

    def calculate_encryption_attribute(self):
        for vertex_index in self.vertices_by_block_type.get(BlockType.RESOURCE.value, []):
            vertex = self.vertices[vertex_index]
            resource_type = vertex.id.split('.')[0]
            encryption_conf = ENCRYPTION_BY_RESOURCE_TYPE.get(resource_type)
            attributes = vertex.get_attribute_dict()
            if encryption_conf:
                is_encrypted, reason = encryption_conf.is_encrypted(attributes)
                # TODO: Does not support possible dependency (i.e. S3 Object being encrypted due to S3 Bucket config)
                vertex.attributes[CustomAttributes.ENCRYPTION] = \
                    EncryptionValues.ENCRYPTED.value if is_encrypted else EncryptionValues.UNENCRYPTED.value
                vertex.attributes[CustomAttributes.ENCRYPTION_DETAILS] = reason
