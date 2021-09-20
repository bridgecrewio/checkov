from copy import deepcopy
from typing import TYPE_CHECKING, Tuple, List, Any, Dict, Optional

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.utils import get_referenced_vertices_in_value, find_all_interpolations
from checkov.cloudformation.graph_builder.variable_rendering.vertex_reference import VertexReference
from checkov.cloudformation.parser.cfn_keywords import IntrinsicFunctions
from checkov.common.graph.graph_builder import Edge, CustomAttributes
from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer

if TYPE_CHECKING:
    from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph


class CloudformationVariableRenderer(VariableRenderer):
    EDGE_EVALUATION_CFN_FUNCTIONS = (
        IntrinsicFunctions.REF, IntrinsicFunctions.FIND_IN_MAP, IntrinsicFunctions.GET_ATT, IntrinsicFunctions.SUB)
    VERTEX_EVALUATION_CFN_FUNCTIONS = (IntrinsicFunctions.SELECT, IntrinsicFunctions.JOIN)

    def __init__(self, local_graph: "CloudformationLocalGraph") -> None:
        super().__init__(local_graph)
        self.edge_evaluation_methods = {
            IntrinsicFunctions.REF: self._evaluate_ref_connection,
            IntrinsicFunctions.FIND_IN_MAP: self._evaluate_findinmap_connection,
            IntrinsicFunctions.GET_ATT: self._evaluate_getatt_connection,
            # ConditionFunctions.IF: self._evaluate_if_connection,
            IntrinsicFunctions.SUB: self._evaluate_sub_connection
        }
        self.vertex_evaluation_methods = {
            IntrinsicFunctions.SELECT: self._evaluate_select_function,
            IntrinsicFunctions.JOIN: self._evaluate_join_function
        }

    """
     This method will evaluate Ref, Fn::FindInMap, Fn::GetAtt, Fn::Sub
    """

    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> None:
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
            cfn_evaluation_function = None
            for curr_evaluation_function in self.EDGE_EVALUATION_CFN_FUNCTIONS:
                if curr_evaluation_function in val_to_eval:
                    cfn_evaluation_function = curr_evaluation_function
                    break
            if cfn_evaluation_function:
                original_value = val_to_eval.get(cfn_evaluation_function, None)

                for edge in edge_list:
                    dest_vertex_attributes = self.local_graph.get_vertex_attributes_by_index(edge.dest)
                    evaluated_value, attribute_at_dest = self.edge_evaluation_methods[cfn_evaluation_function](
                        val_to_eval[cfn_evaluation_function], dest_vertex_attributes)
                    if evaluated_value and evaluated_value != original_value:
                        val_to_eval[cfn_evaluation_function] = evaluated_value
                        self.local_graph.update_vertex_attribute(
                            vertex_index=edge.origin,
                            attribute_key=edge.label,
                            attribute_value=evaluated_value,
                            change_origin_id=edge.dest,
                            attribute_at_dest=attribute_at_dest
                        )

    """
        This method will evaluate Fn::Select, Fn::Join
    """

    def _render_variables_from_vertices(self) -> None:
        for vertex in self.local_graph.vertices:
            for attr_key, attr_value in vertex.attributes.items():
                # Iterating on Fn::Join, Fn::Select and checking if they are
                # in the current attribute value
                cfn_evaluation_function = next(
                    (curr_evaluation_function
                     for curr_evaluation_function in self.VERTEX_EVALUATION_CFN_FUNCTIONS
                     if isinstance(attr_value, dict) and curr_evaluation_function in attr_value),
                    None
                )
                if cfn_evaluation_function:
                    # Found Fn::Join or Fn::Select to evaluate
                    val_to_eval = attr_value[cfn_evaluation_function]
                    evaluated_value = self.vertex_evaluation_methods[cfn_evaluation_function](val_to_eval)
                    if evaluated_value is not None:
                        vertex.update_attribute(
                            attribute_key=attr_key, attribute_value=evaluated_value, change_origin_id=None,
                            previous_breadcrumbs=[], attribute_at_dest=None
                        )

    """
    Valid value for the Select function is:
    [index, [item1, item2, ...]]
    while index could an int or a string representing an int
    and the list could be a list or a string representing a list
    """

    @staticmethod
    def _evaluate_select_function(value: str) -> Optional[str]:
        evaluated_value = None
        if len(value) != 2:
            return None
        idx_to_select = value[0]
        selection_list = value[1]
        if not isinstance(selection_list, (str, list)):
            return None
        if isinstance(selection_list, str):
            selection_list = selection_list.split(', ')
        # convert idx_to_select to int if possible cause it might be a str_node
        if isinstance(idx_to_select, str) and str.isdecimal(idx_to_select):
            idx_to_select = int(idx_to_select)
        if isinstance(idx_to_select, int) and isinstance(selection_list, list) \
                and 0 <= idx_to_select < len(selection_list):
            evaluated_value = selection_list[idx_to_select]
            if 'Fn::' in evaluated_value or "AWS::" in evaluated_value or 'Ref' in evaluated_value:
                # Don't render if a non-evaluated value has been selected
                return None
        return evaluated_value

    """
        Valid value for the Join function is:
        [ delimiter, [ comma-delimited list of values ] ]
        the list could be a list or a string representing a list
        """

    @staticmethod
    def _evaluate_join_function(value: str) -> Optional[str]:
        evaluated_value = None
        if len(value) != 2:
            return None
        delimiter = value[0]
        values_list = value[1]
        if not isinstance(values_list, (str, list)):
            return None
        if isinstance(values_list, str):
            values_list = values_list.split(', ')
        if isinstance(delimiter, str) and isinstance(values_list, list):
            for curr_value in values_list:
                if isinstance(curr_value, dict):
                    # non-evaluated values then don't render
                    return None
            evaluated_value = delimiter.join(values_list)
        return evaluated_value

    @staticmethod
    def _evaluate_ref_connection(value: str, dest_vertex_attributes: Dict[str, Any]) -> (Optional[str], Optional[str]):
        # in case of Ref we take only Parameter's default value
        attribute_at_dest = 'Default'
        evaluated_value = dest_vertex_attributes.get(attribute_at_dest)
        if (
                evaluated_value and
                value == dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and
                dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.PARAMETERS
        ):
            return str(evaluated_value), attribute_at_dest
        return None, None

    @staticmethod
    def _evaluate_findinmap_connection(value: List[str], dest_vertex_attributes: Dict[str, Any]) -> (
            Optional[str], Optional[str]):
        # value = [ "MapName", "TopLevelKey", "SecondLevelKey"]
        if isinstance(value, list) and len(value) == 3:
            map_name = value[0]
            top_level_key = value[1]
            second_level_key = value[2]
            attribute_at_dest = f'{top_level_key}.{second_level_key}'
            evaluated_value = dest_vertex_attributes.get(attribute_at_dest)

            if evaluated_value and \
                    all(isinstance(element, str) for element in value) and \
                    map_name == dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and \
                    dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.MAPPINGS:
                return str(evaluated_value), attribute_at_dest

        return None, None

    @staticmethod
    def _evaluate_getatt_connection(value: List[str], dest_vertex_attributes: Dict[str, Any]) -> (
            Optional[str], Optional[str]):
        # value = [ "logicalNameOfResource", "attributeName" ]
        if isinstance(value, list) and len(value) == 2:
            resource_name = value[0]
            attribute_name = value[1]
            dest_name = dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME).split('.')[-1]
            attribute_at_dest = attribute_name
            evaluated_value = dest_vertex_attributes.get(
                attribute_at_dest)  # we extract only build time atts, not runtime

            if evaluated_value and \
                    all(isinstance(element, str) for element in value) and \
                    resource_name == dest_name and \
                    dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.RESOURCE:
                return str(evaluated_value), attribute_at_dest

        return None, None

    def _evaluate_sub_connection(self, value: str, dest_vertex_attributes: Dict[str, Any]) -> (
            Optional[str], Optional[str]):
        if isinstance(value, list):
            # TODO: Render values of list type
            return None, None
        evaluated_value = None
        attribute_at_dest = None

        # value = '..${ref/getatt}..${ref/getatt}..${ref/getatt}..'
        block_name = dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME, None)
        block_type = dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE, None)
        if block_type == BlockType.RESOURCE:
            block_name = block_name.split('.')[-1]

        vars_set = set(find_all_interpolations(value))  # a list of parameters and resources.at.attribute
        vars_list = [var for var in vars_set if block_name in var]  # get only relevant interpolations

        if block_type == BlockType.PARAMETERS:
            block_evaluated_value, block_attribute = self._evaluate_ref_connection(block_name, dest_vertex_attributes)
            if block_evaluated_value:
                evaluated_value = value.replace(f'${{{block_name}}}', block_evaluated_value)
                attribute_at_dest = block_attribute
                evaluated_value = evaluated_value if evaluated_value else value
        elif block_type == BlockType.RESOURCE and block_name:
            for var in vars_list:
                split_var = var.split('.')
                block_evaluated_value, block_attribute = self._evaluate_getatt_connection(split_var,
                                                                                          dest_vertex_attributes)
                if block_evaluated_value:
                    evaluated_value = value.replace(f'${{{var}}}', block_evaluated_value)
                    attribute_at_dest = block_attribute
                    evaluated_value = evaluated_value if evaluated_value else value

        return evaluated_value, attribute_at_dest

    # def _evaluate_if_connection(self, value: List[str], dest_vertex_attributes: Dict[str, Any]) -> Optional[str]:
    #     evaluated_value = None
    #     condition_name = value[0]
    #     value_if_true = value[1]
    #     value_if_false = value[2]
    #
    #     if all(isinstance(element, str) for element in value) and \
    #             condition_name == dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and \
    #             dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.CONDITIONS:
    #         evaluated_value = self._evaluate_condition(value)
    #         evaluated_value = str(evaluated_value) if evaluated_value else None
    #     return evaluated_value

    # def _evaluate_condition(self, value: List[str]) -> Optional[bool]:
    #     # value = [condition_name, value_if_true, value_if_false]
    #     return None

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

        updated_resources_blocks_name_map = {}
        for resource_name, blocks_list in resources_blocks_name_map.items():
            shortened_resource_name = resource_name.split('.')[
                -1]  # Trims AWS::X::Y.ResourceName and leaves us with ResoruceName
            updated_resources_blocks_name_map[shortened_resource_name] = blocks_list
        vertices_block_name_map[BlockType.RESOURCE] = updated_resources_blocks_name_map
        return vertices_block_name_map
