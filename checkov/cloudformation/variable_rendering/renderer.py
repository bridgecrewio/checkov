from typing import TYPE_CHECKING, Tuple, List, Any, Dict, Optional, Union, Callable, overload, Set
from copy import deepcopy

from checkov.cloudformation.parser.cfn_keywords import IntrinsicFunctions, ConditionFunctions
from checkov.common.graph.graph_builder import Edge, CustomAttributes
from checkov.common.graph.variable_rendering.renderer import VariableRenderer
from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.utils import VertexReference, get_referenced_vertices_in_value, find_all_interpolations

if TYPE_CHECKING:
    from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph


class CloudformationVariableRenderer(VariableRenderer):
    EVALUATION_CFN_FUNCTIONS = (
        IntrinsicFunctions.REF, IntrinsicFunctions.FIND_IN_MAP, IntrinsicFunctions.GET_ATT, ConditionFunctions.IF,
        IntrinsicFunctions.SUB)

    def __init__(self, local_graph: "CloudformationLocalGraph") -> None:
        super().__init__(local_graph)
        self.evaluation_methods = {
            IntrinsicFunctions.REF: self._evaluate_ref_connection,
            IntrinsicFunctions.FIND_IN_MAP: self._evaluate_findinmap_connection,
            IntrinsicFunctions.GET_ATT: self._evaluate_getatt_connection,
            ConditionFunctions.IF: self._evaluate_if_connection,
            IntrinsicFunctions.SUB: self._evaluate_sub_connection
        }

    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> None:
        multiple_edges = len(edge_list) > 1
        edge = edge_list[0]
        origin_vertex_attributes = self.local_graph.vertices[edge.origin].attributes
        val_to_eval = deepcopy(origin_vertex_attributes.get(edge.label, ""))
        vertices_block_name_map = self._extract_vertices_block_name_map()

        referenced_vertices = get_referenced_vertices_in_value(
            value=val_to_eval, vertices_block_name_map=vertices_block_name_map
        )
        if not referenced_vertices:
            # DependsOn or Condition connections
            pass

        if referenced_vertices:
            # Ref, GetAtt, FindInMap, If, Sub connections
            evaluation_function = None
            for curr_evaluation_function in self.EVALUATION_CFN_FUNCTIONS:
                if curr_evaluation_function in val_to_eval:
                    evaluation_function = curr_evaluation_function
            if evaluation_function:
                original_value = val_to_eval.get(evaluation_function, None)
                evaluated_value = original_value

                for edge in edge_list:
                    dest_vertex_attributes = self.local_graph.get_vertex_attributes_by_index(edge.dest)
                    evaluated_value = self.evaluation_methods[evaluation_function](evaluated_value, dest_vertex_attributes)
                    if evaluated_value:
                        val_to_eval[evaluation_function] = evaluated_value

                if evaluated_value and evaluated_value != original_value:
                    self.update_evaluated_value(
                        changed_attribute_key=edge.label,
                        changed_attribute_value=evaluated_value,
                        vertex=edge.origin,
                        change_origin_id=edge.dest,
                        attribute_at_dest=edge.label,
                    )
                    print('here')

    @staticmethod
    def _evaluate_ref_connection(value: str, dest_vertex_attributes) -> Optional[str]:
        evaluated_value = None

        # in case of Ref we take only Parameter's default value
        if value == dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and dest_vertex_attributes.get(
                CustomAttributes.BLOCK_TYPE) == BlockType.PARAMETERS:
            evaluated_value = dest_vertex_attributes.get('Default', None)
        return evaluated_value

    @staticmethod
    def _evaluate_findinmap_connection(value: List[str], dest_vertex_attributes) -> Optional[str]:
        evaluated_value = None

        # value = [ "MapName", "TopLevelKey", "SecondLevelKey"]
        if isinstance(value, list) and len(value) == 3:
            map_name = value[0]
            top_level_key = value[1]
            second_level_key = value[2]

            if all(isinstance(element, str) for element in value) and \
                    map_name == dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and \
                    dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.MAPPINGS:
                evaluated_value = dest_vertex_attributes.get(f'{top_level_key}.{second_level_key}', None)
        return evaluated_value

    @staticmethod
    def _evaluate_getatt_connection(value: List[str], dest_vertex_attributes) -> Optional[str]:
        evaluated_value = None

        # value = [ "logicalNameOfResource", "attributeName" ]
        if isinstance(value, list) and len(value) == 2:
            resource_name = value[0]
            attribute_name = value[1]
            dest_name = dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME).split('.')[-1]

            if all(isinstance(element, str) for element in value) and \
                    resource_name == dest_name and \
                    dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.RESOURCE:
                evaluated_value = dest_vertex_attributes.get(attribute_name, None)  # we extract only build time atts, not runtime
        return evaluated_value

    def _evaluate_sub_connection(self, value: str, dest_vertex_attributes) -> Optional[str]:
        evaluated_value = None

        # value = '..${ref/getatt}..${ref/getatt}..${ref/getatt}..'
        block_name = dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME, None)
        block_type = dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE, None)
        if block_type == BlockType.RESOURCE:
            block_name = block_name.split('.')[-1]

        vars_list = find_all_interpolations(value) # a list of parameters and resources.at.attribute
        vars_list = [var for var in vars_list if block_name in var] # get only relevate interpolations

        if block_type == BlockType.PARAMETERS:
            block_evaluated_value = self._evaluate_ref_connection(block_name, dest_vertex_attributes)
            if block_evaluated_value:
                evaluated_value = value.replace(f'${{{block_name}}}', block_evaluated_value)
        elif block_type == BlockType.RESOURCE and block_name:
            for var in vars_list:
                split_var = var.split('.')
                block_evaluated_value = self._evaluate_getatt_connection(split_var, dest_vertex_attributes)
                if block_evaluated_value:
                    evaluated_value = value.replace(f'${{{var}}}', block_evaluated_value)

        return evaluated_value

    def _evaluate_if_connection(self, value: List[str], dest_vertex_attributes) -> Optional[str]:
        evaluated_val = None
        condition_name = value[0]
        value_if_true = value[1]
        value_if_false = value[2]

        if all(isinstance(element, str) for element in value) and \
                condition_name == dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and \
                dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.CONDITIONS:
            evaluated_val = self._evaluate_condition(value)
        return evaluated_val

    def _evaluate_condition(self, value: List[str]) -> Optional[bool]:
        # value = [condition_name, value_if_true, value_if_false]
        return None

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
        self.local_graph.update_vertex_attribute(
            vertex, changed_attribute_key, changed_attribute_value, change_origin_id, attribute_at_dest
        )


    @staticmethod
    def find_path_from_referenced_vertices(
            referenced_vertices: List[VertexReference], vertex_attributes: Dict[str, Any]
    ) -> Tuple[List[str], str]:
        """
        :param referenced_vertices: an array of VertexReference
        :param vertex_attributes: attributes to search
        :return attribute_path: [] if referenced_vertices does not contain vertex_attributes,
                                else the path to the searched attribute
        :return origin_value
        """
        for vertex_reference in referenced_vertices:
            block_type = vertex_reference.block_type
            attribute_path = vertex_reference.sub_parts
            if vertex_attributes[CustomAttributes.BLOCK_TYPE] == block_type:
                for i in range(len(attribute_path)):
                    name = ".".join(attribute_path[: i + 1])
                    if vertex_attributes[CustomAttributes.BLOCK_NAME] == name:
                        return attribute_path, vertex_reference.origin_value
        return [], ""

    def _extract_vertices_block_name_map(self) -> Dict[str, Dict[str, List[int]]]:
        vertices_block_name_map = deepcopy(self.local_graph.vertices_block_name_map)
        resources_blocks_name_map = vertices_block_name_map[BlockType.RESOURCE]

        for resource_name, blocks_list in resources_blocks_name_map.items():
            resources_blocks_name_map.pop(resource_name)
            shortened_resource_name = resource_name.split('.')[-1]  # Trims AWS::X::Y.ResourceName and leaves us with ResoruceName
            resources_blocks_name_map[shortened_resource_name] = blocks_list
        return vertices_block_name_map

