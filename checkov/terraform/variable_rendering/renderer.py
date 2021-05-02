import logging
import os
from copy import deepcopy

from lark.tree import Tree

from checkov.terraform.checks.utils.utils import run_function_multithreaded, get_referenced_vertices_in_value, \
    join_trimmed_strings, remove_index_pattern_from_str, calculate_hash, attribute_has_nested_attributes
from checkov.terraform.graph_builder.graph_components.attribute_names import CustomAttributes, reserved_attribute_names
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.variable_rendering.evaluate_terraform import replace_string_value, evaluate_terraform

ATTRIBUTES_NO_EVAL = ['template_body', 'template']


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
        self.done_edges_by_origin_vertex = {}
        self.replace_cache = [{}] * len(local_graph.vertices)

    def render_variables_from_local_graph(self):
        # find vertices with out-degree = 0 and in-degree > 0
        end_vertices_indexes = self.local_graph.get_vertices_with_degrees_conditions(
            out_degree_cond=lambda degree: degree == 0,
            in_degree_cond=lambda degree: degree > 0)

        # all the edges entering `end_vertices`
        edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
        loops = 0
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
            for edge in edges_to_render:
                origin = edge.origin
                if origin not in self.done_edges_by_origin_vertex:
                    self.done_edges_by_origin_vertex[origin] = []
                self.done_edges_by_origin_vertex[origin].append(edge)

            for edge in edges_to_render:
                origin_vertex_index = edge.origin
                out_edges = self.local_graph.out_edges.get(origin_vertex_index)
                if all(e in self.done_edges_by_origin_vertex.get(origin_vertex_index, []) for e in out_edges):
                    end_vertices_indexes.append(origin_vertex_index)
            edges_to_render = self.local_graph.get_in_edges(end_vertices_indexes)
            edges_to_render = list(set([edge for edge in edges_to_render if edge not in self.done_edges_by_origin_vertex.get(edge.origin, [])]))
            loops += 1
            if loops >= 50:
                logging.warning(f"Reached 50 graph edge iterations, breaking. Module: {self.local_graph.module.source_dir}")
                break

        self.local_graph.update_vertices_configs()
        logging.info('done evaluating edges')
        self.evaluate_non_rendered_values()

    def _edge_evaluation_task(self, edges):
        edges = edges[0]
        self.evaluate_vertex_attribute_from_edge(edges)
        return edges

    def evaluate_vertex_attribute_from_edge(self, edge_list):
        multiple_edges = len(edge_list) > 1
        edge = edge_list[0]
        origin_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        val_to_eval = deepcopy(origin_vertex_attributes.get(edge.label, ''))

        referenced_vertices = get_referenced_vertices_in_value(value=val_to_eval, aliases={},
                                                               resources_types=self.local_graph.get_resources_types_in_graph())
        if not referenced_vertices:
            origin_vertex = self.local_graph.vertices[edge.origin]
            destination_vertex = self.local_graph.vertices[edge.dest]
            if origin_vertex.block_type == BlockType.VARIABLE and destination_vertex.block_type == BlockType.MODULE:
                self.update_evaluated_value(changed_attribute_key=edge.label,
                                            changed_attribute_value=destination_vertex.attributes[origin_vertex.name], vertex=edge.origin,
                                            change_origin_id=edge.dest, attribute_at_dest=edge.label)
                return
            if origin_vertex.block_type == BlockType.VARIABLE and destination_vertex.block_type == BlockType.TF_VARIABLE:
                self.update_evaluated_value(changed_attribute_key=edge.label,
                                            changed_attribute_value=destination_vertex.attributes['default'],
                                            vertex=edge.origin,
                                            change_origin_id=edge.dest, attribute_at_dest=edge.label)
                return

        modified_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        val_to_eval = deepcopy(modified_vertex_attributes.get(edge.label, ''))
        origin_val = deepcopy(val_to_eval)
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
                    val_to_eval = self.replace_value(edge, val_to_eval, replaced_key, evaluated_attribute_value, True)
                if not multiple_edges and val_to_eval != origin_val:
                    self.update_evaluated_value(changed_attribute_key=edge.label,
                                                changed_attribute_value=val_to_eval, vertex=edge.origin, change_origin_id=edge.dest, attribute_at_dest=key_path_in_dest_vertex)

        if multiple_edges and val_to_eval != origin_val:
            self.update_evaluated_value(changed_attribute_key=edge.label,
                                        changed_attribute_value=val_to_eval, vertex=edge.origin, change_origin_id=edge.dest, attribute_at_dest=first_key_path)

        # Avoid loops on output => output edges
        if self.local_graph.vertices[edge.origin].block_type == BlockType.OUTPUT and \
                self.local_graph.vertices[edge.dest].block_type == BlockType.OUTPUT:
            if edge.origin not in self.done_edges_by_origin_vertex:
                self.done_edges_by_origin_vertex[edge.origin] = []
            self.done_edges_by_origin_vertex[edge.origin].append(edge)

    def extract_value_from_vertex(self, key_path, attributes):
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

        if attributes.get(CustomAttributes.BLOCK_TYPE) in [BlockType.VARIABLE.value, BlockType.TF_VARIABLE.value]:
            default_val = attributes.get('default')
            value = None
            if isinstance(default_val, dict):
                value = self.extract_value_from_vertex(key_path, default_val)
            return default_val if not value else value
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
        str_to_evaluate = str(changed_attribute_value) if changed_attribute_key in ATTRIBUTES_NO_EVAL else f'"{str(changed_attribute_value)}"'
        str_to_evaluate = str_to_evaluate.replace("\\\\", "\\")
        evaluated_attribute_value = str_to_evaluate if changed_attribute_key in ATTRIBUTES_NO_EVAL else evaluate_terraform(str_to_evaluate)
        self.local_graph.update_vertex_attribute(vertex, changed_attribute_key, evaluated_attribute_value, change_origin_id, attribute_at_dest)

    def evaluate_vertices_attributes(self):
        for vertex in self.local_graph.vertices:
            decoded_attributes = vertex.get_decoded_attribute_dict()
            for attr in decoded_attributes:
                if attr in vertex.changed_attributes:
                    continue
                origin_value = decoded_attributes[attr]
                if not isinstance(origin_value, str):
                    continue
                evaluated_attribute_value = evaluate_terraform(origin_value)
                if origin_value != evaluated_attribute_value:
                    vertex.update_inner_attribute(attr, vertex.attributes, evaluated_attribute_value)

    @staticmethod
    def group_edges_by_origin_and_label(edges):
        edge_groups = {}
        for edge in edges:
            origin_and_label_hash = calculate_hash(f'{edge.origin}{edge.label}')
            if not edge_groups.get(origin_and_label_hash):
                edge_groups[origin_and_label_hash] = []
            edge_groups[origin_and_label_hash].append(edge)
        return list(edge_groups.values())

    def replace_value(self, edge, original_val, replaced_key, replaced_value, keep_origin, count=0):
        if count > 1:
            return original_val
        new_val = replace_string_value(original_str=original_val, str_to_replace=replaced_key,
                                       replaced_value=replaced_value, keep_origin=keep_origin)
        curr_cache = self.replace_cache[edge.origin].get(edge.label, {}).get(replaced_key, [])
        # not_containing_dot = '.' not in new_val
        not_containing_dot = '.' not in str(new_val)
        if not_containing_dot or new_val not in curr_cache or (len(curr_cache) > 0 and curr_cache[-1] != new_val):
            if not self.replace_cache[edge.origin].get(edge.label, {}):
                self.replace_cache[edge.origin][edge.label] = {}
            if not curr_cache:
                self.replace_cache[edge.origin][edge.label][replaced_key] = []
            self.replace_cache[edge.origin][edge.label][replaced_key].append(new_val)
            return new_val
        else:
            return self.replace_value(edge, original_val, replaced_key, replaced_value, not keep_origin, count + 1)

    def evaluate_non_rendered_values(self):
        for vertex in self.local_graph.vertices:
            changed_attributes = {}
            attributes = {}
            vertex.get_origin_attributes(attributes)
            for attribute in filter(lambda attr: attr not in reserved_attribute_names and not attribute_has_nested_attributes(attr, vertex.attributes), vertex.attributes):
                curr_val = vertex.attributes.get(attribute)
                lst_curr_val = curr_val
                if not isinstance(lst_curr_val, list):
                    lst_curr_val = [lst_curr_val]
                if len(lst_curr_val) > 0 and isinstance(lst_curr_val[0], Tree):
                    lst_curr_val[0] = str(lst_curr_val[0])
                evaluated_lst = []
                for inner_val in lst_curr_val:
                    if isinstance(inner_val, str) and not any(c in inner_val for c in ["{", "}", "[", "]", "="])\
                            or attribute in ATTRIBUTES_NO_EVAL:
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

    def evaluate_value(self, val):
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
                evaluated_val.add(self.evaluate_value(v))
        else:
            evaluated_val = {}
            for k, v in val.items():
                evaluated_key = self.evaluate_value(k)
                evaluated_val[evaluated_key] = self.evaluate_value(v)
        return evaluated_val
