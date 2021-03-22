import logging
import os
from copy import deepcopy

from checkov.graph.terraform.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.graph.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.graph.terraform.utils.utils import get_referenced_vertices_in_value, run_function_multithreaded, calculate_hash, \
    join_trimmed_strings, remove_interpolation, remove_index_pattern_from_str, remove_function_calls_from_str
from checkov.graph.terraform.variable_rendering.evaluate_terraform import replace_string_value, evaluate_terraform


class VariableRenderer:
    def __init__(self, local_graph):
        self.local_graph = local_graph
        run_async = os.environ.get('RENDER_VARIABLES_ASYNC')
        if not run_async:
            run_async = True
        else:
            run_async = True if run_async == 'True' else False
        self.run_async = run_async
        max_workers = os.environ.get('RENDER_ASYNC_MAX_WORKERS')
        if not max_workers:
            max_workers = 50
        else:
            max_workers = int(max_workers)
        self.max_workers = max_workers
        self.done_edges = []

    def render_variables_from_local_graph(self):
        # find vertices with out-degree = 0 and in-degree > 0
        end_vertices_indexes = self.local_graph.get_vertices_with_degrees_conditions(
            out_degree_cond=lambda degree: degree == 0,
            in_degree_cond=lambda degree: degree > 0)

        # all the edges entering `end_vertices`
        edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
        while len(edges_to_render) > 0:
            logging.info(f'evaluating {len(edges_to_render)} edges')
            # group edges that have the same origin and label together
            edges_groups = self.group_edges_by_origin_and_label(edges_to_render)
            if self.run_async:
                run_function_multithreaded(func=self._edge_evaluation_task, data=edges_groups, max_group_size=1,
                                           num_of_workers=self.max_workers)
            else:
                for edge_group in edges_groups:
                    self._edge_evaluation_task([edge_group])
            end_vertices_indexes = list(set([edge.origin for edge in edges_to_render]))
            edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
            edges_to_render = [edge for edge in edges_to_render if edge not in self.done_edges]
        self.local_graph.update_vertices_configs()
        logging.info('done evaluating edges')

    def _edge_evaluation_task(self, edges):
        edges = edges[0]
        self.evaluate_vertex_attribute_from_edge(edges)
        return edges

    def evaluate_vertex_attribute_from_edge(self, edge_list):
        multiple_edges = len(edge_list) > 1
        edge = edge_list[0]
        origin_vertex_attributes = self.local_graph.get_vertex_attributes_by_index(edge.origin)
        val_to_eval = deepcopy(origin_vertex_attributes.get(edge.label, ''))

        referenced_vertices = get_referenced_vertices_in_value(value=val_to_eval, aliases={},
                                                               resources_types=self.local_graph.get_resources_types_in_graph(),
                                                               cleanup_functions=[remove_function_calls_from_str,
                                                                                  remove_interpolation])
        first_key_path = None
        if referenced_vertices:
            for edge in edge_list:
                dest_vertex_attributes = self.local_graph.get_vertex_attributes_by_index(edge.dest)
                key_path_in_dest_vertex, replaced_key = self.find_path_from_referenced_vertices(referenced_vertices,
                                                                                                  dest_vertex_attributes)
                if not key_path_in_dest_vertex or not replaced_key:
                    continue
                if not first_key_path:
                    first_key_path = key_path_in_dest_vertex

                evaluated_attribute_value = self.extract_value_from_vertex(key_path_in_dest_vertex,
                                                                           dest_vertex_attributes)
                if evaluated_attribute_value is not None:
                    val_to_eval = replace_string_value(original_str=val_to_eval, str_to_replace=replaced_key, replaced_value=str(evaluated_attribute_value))
                if not multiple_edges:
                    self.update_evaluated_value(changed_attribute_key=edge.label,
                                                changed_attribute_value=val_to_eval, vertex=edge.origin, change_origin_id=edge.dest, attribute_at_dest=key_path_in_dest_vertex)
        if multiple_edges:
            self.update_evaluated_value(changed_attribute_key=edge.label,
                                        changed_attribute_value=val_to_eval, vertex=edge.origin, change_origin_id=edge.dest, attribute_at_dest=first_key_path)

    @staticmethod
    def extract_value_from_vertex(key_path, attributes):

        for i in range(len(key_path)):
            key = join_trimmed_strings(char_to_join=".", str_lst=key_path, num_to_trim=i)
            value = attributes.get(key, None)
            if value is not None:
                return value

        reversed_key_path = deepcopy(key_path)
        reversed_key_path.reverse()
        for i in range(len(reversed_key_path)):
            key = join_trimmed_strings(char_to_join=".", str_lst=reversed_key_path, num_to_trim=i)
            value = attributes.get(key, None)
            if value is not None:
                return value

        if attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.VARIABLE.value:
            return attributes.get('default')
        if attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.OUTPUT.value:
            return attributes.get('value')
        return None

    @staticmethod
    def find_path_from_referenced_vertices(referenced_vertices, vertex_attributes):
        """
        :param referenced_vertices: an array of VertexReference
        :param vertex_attributes: attributes to search
        :return attribute_path: [] if referenced_vertices does not contain vertex_attributes,
                                else the path to the searched attribute: ['vpc_id']
        :return origin_value
        """
        for vertex_reference in referenced_vertices:
            block_type = vertex_reference.block_type.value
            attribute_path = vertex_reference.sub_parts
            copy_of_attribute_path = deepcopy(attribute_path)
            if vertex_attributes[CustomAttributes.BLOCK_TYPE] == block_type:
                for i in range(len(copy_of_attribute_path)):
                    copy_of_attribute_path[i] = remove_index_pattern_from_str(copy_of_attribute_path[i])
                    name = ".".join(copy_of_attribute_path[:i + 1])
                    if vertex_attributes[CustomAttributes.BLOCK_NAME] == name:
                        return attribute_path, vertex_reference.origin_value
            elif block_type == BlockType.MODULE:
                copy_of_attribute_path.reverse()
                for i in range(len(copy_of_attribute_path)):
                    copy_of_attribute_path[i] = remove_index_pattern_from_str(copy_of_attribute_path[i])
                    name = ".".join(copy_of_attribute_path[:i + 1])
                    if vertex_attributes[CustomAttributes.BLOCK_NAME] == name:
                        return name.split('.'), vertex_reference.origin_value
        return [], ''

    def update_evaluated_value(self, changed_attribute_key, changed_attribute_value, vertex, change_origin_id, attribute_at_dest=None):
        """
        The function updates the value of changed_attribute_key with changed_attribute_value for vertex
        """
        references_vertices = get_referenced_vertices_in_value(value=changed_attribute_value, aliases={},
                                                               resources_types=self.local_graph.get_resources_types_in_graph())
        if not references_vertices:
            evaluated_attribute_value = evaluate_terraform(f'"{str(changed_attribute_value)}"')
            self.local_graph.update_vertex_attribute(vertex, changed_attribute_key, evaluated_attribute_value, change_origin_id, attribute_at_dest)

    @staticmethod
    def group_edges_by_origin_and_label(edges):
        edge_groups = {}
        for edge in edges:
            origin_and_label_hash = calculate_hash(f'{edge.origin}{edge.label}')
            if not edge_groups.get(origin_and_label_hash):
                edge_groups[origin_and_label_hash] = []
            edge_groups[origin_and_label_hash].append(edge)
        return list(edge_groups.values())
