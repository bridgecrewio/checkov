from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Tuple, List, Any, Dict, Optional, Callable, TypedDict

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.utils import get_referenced_vertices_in_value, find_all_interpolations
from checkov.cloudformation.graph_builder.variable_rendering.vertex_reference import VertexReference
from checkov.cloudformation.parser.cfn_keywords import IntrinsicFunctions, ConditionFunctions, PseudoParameters
from checkov.common.graph.graph_builder import Edge, CustomAttributes
from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.variable_rendering.renderer import VariableRenderer
from checkov.common.parsers.node import StrNode
from checkov.common.util.data_structures_utils import pickle_deepcopy

if TYPE_CHECKING:
    from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock
    from checkov.cloudformation.graph_builder.local_graph import CloudformationLocalGraph
    from typing_extensions import TypeAlias

_EdgeEvaluationMethodsEntry: TypeAlias = "dict[str, Callable[[Any, dict[str, Any]], tuple[str | None, str | None]]]"
_VertexEvaluationMethodsEntry: TypeAlias = "dict[str, Callable[[Any], str | None]]"


class _EvaluatedEdge(TypedDict):
    vertex_index: int
    attribute_key: str
    attribute_value: Any
    change_origin_id: int | None
    attribute_at_dest: str | None


class CloudformationVariableRenderer(VariableRenderer["CloudformationLocalGraph"]):
    EDGE_EVALUATION_CFN_FUNCTIONS = (
        IntrinsicFunctions.REF, IntrinsicFunctions.FIND_IN_MAP, IntrinsicFunctions.GET_ATT,
        IntrinsicFunctions.SUB, ConditionFunctions.IF)
    VERTEX_EVALUATION_CFN_FUNCTIONS = (IntrinsicFunctions.SELECT, IntrinsicFunctions.JOIN)
    CONDITIONS_EVALUATED_FUNCTIONS = (ConditionFunctions.OR, ConditionFunctions.AND, ConditionFunctions.EQUALS,
                                      ConditionFunctions.NOT, IntrinsicFunctions.CONDITION)

    def __init__(self, local_graph: "CloudformationLocalGraph") -> None:
        super().__init__(local_graph)
        self.edge_evaluation_methods: _EdgeEvaluationMethodsEntry = {
            IntrinsicFunctions.REF: self._evaluate_ref_connection,
            IntrinsicFunctions.FIND_IN_MAP: self._evaluate_findinmap_connection,
            IntrinsicFunctions.GET_ATT: self._evaluate_getatt_connection,
            IntrinsicFunctions.SUB: self._evaluate_sub_connection
        }
        self.vertex_evaluation_methods: "dict[str, Callable[[Any], str | None]]" = {
            IntrinsicFunctions.SELECT: self._evaluate_select_function,
            IntrinsicFunctions.JOIN: self._evaluate_join_function
        }
        self.vertices_block_name_map = self._extract_vertices_block_name_map()

    """
     This method will evaluate Ref, Fn::FindInMap, Fn::GetAtt, Fn::Sub
    """

    def evaluate_vertex_attribute_from_edge(self, edge_list: List[Edge]) -> None:
        edge = edge_list[0]
        origin_vertex = self.local_graph.vertices[edge.origin]
        origin_vertex_attributes = origin_vertex.attributes
        val_to_eval = pickle_deepcopy(origin_vertex_attributes.get(edge.label, ""))

        referenced_vertices = get_referenced_vertices_in_value(
            value=val_to_eval, vertices_block_name_map=self.vertices_block_name_map
        )
        if not referenced_vertices:
            # DependsOn or Condition connections
            self._handle_dependson_condition_connections(edge, origin_vertex)
        elif isinstance(val_to_eval, dict):
            self._handle_edge_list_evaluation_functions(edge_list, origin_vertex, val_to_eval)

    """
        This method will evaluate Fn::Select, Fn::Join
    """

    def _render_variables_from_vertices(self) -> None:
        for vertex in self.local_graph.vertices:
            vertex_attributes = pickle_deepcopy(vertex.attributes)
            for attr_key, attr_value in vertex_attributes.items():
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
    def _evaluate_select_function(value: list[int | str | list[str]]) -> Optional[str]:
        evaluated_value = None
        if len(value) != 2:
            return None

        idx_to_select = value[0]
        if not isinstance(idx_to_select, (int, str)):
            return None

        selection_list = value[1]
        if not isinstance(selection_list, (str, list)):
            return None

        if isinstance(selection_list, str):
            selection_list = selection_list.split(', ')
        # convert idx_to_select to int if possible because it might be a str_node
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
    def _evaluate_join_function(value: list[str | list[str]]) -> Optional[str]:
        evaluated_value = None
        if len(value) != 2:
            return None
        delimiter = value[0]
        values_list = value[1]
        if not isinstance(values_list, (str, list)):
            return None
        if isinstance(values_list, str):
            values_list = values_list.split(', ')
        for inner_value in values_list:
            if not isinstance(inner_value, str):
                return None
        if isinstance(delimiter, str) and isinstance(values_list, list):
            for curr_value in values_list:
                if isinstance(curr_value, dict):
                    # non-evaluated values then don't render
                    return None
            evaluated_value = delimiter.join(values_list)
        return evaluated_value

    @staticmethod
    def _evaluate_ref_connection(value: Any, dest_vertex_attributes: Dict[str, Any]) -> tuple[str | None, str | None]:
        # in case of Ref we take only Parameter's default value
        attribute_at_dest = 'Default'
        evaluated_value = dest_vertex_attributes.get(attribute_at_dest)
        if (
                evaluated_value is not None and
                value == dest_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and
                dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.PARAMETERS
        ):
            return str(evaluated_value), attribute_at_dest
        return None, None

    def _fetch_vertex_attributes(self, block_name: str, block_type: str) -> dict[str, Any] | None:
        vertex_attributes = None
        vertex_index_list = self.local_graph.vertices_block_name_map.get(block_type, {}).get(block_name, None)
        if isinstance(vertex_index_list, list):
            vertex_index = vertex_index_list[0]
            vertex_attributes = self.local_graph.get_vertex_attributes_by_index(vertex_index)
        return vertex_attributes

    def _evaluate_condition_by_name(self, condition_name: str) -> Optional[bool]:
        """
        Evaluate CFN condition by the condition name.
        This method simply fetches the vertex from the local graph by the condition name,
        and calls the method _evaluate_condition_by_vertex_attributes
        """

        evaluated_condition = None
        condition_vertex_attributes = self._fetch_vertex_attributes(condition_name, BlockType.CONDITIONS)
        if condition_vertex_attributes:
            evaluated_condition = self._evaluate_condition_by_vertex_attributes(condition_vertex_attributes)
        return evaluated_condition

    def _evaluate_condition_by_vertex_attributes(self, vertex_attributes: Dict[str, Any]) -> Optional[bool]:
        """
        Evaluate CFN vertex condition by the vertex's attributes.
        This method searches for a condition function in the attributes, and when found,
        calls the method _evaluate_condition with the condition found and its value to evaluate
        """

        condition_to_evaluate, value_to_evaluate = next(
            ((current_condition_function, vertex_attributes[current_condition_function])
             for current_condition_function in self.CONDITIONS_EVALUATED_FUNCTIONS
             if current_condition_function in vertex_attributes),
            (None, None))

        return self._evaluate_condition(condition_to_evaluate, value_to_evaluate)

    def _evaluate_condition(self, condition_fn: str | None, value: Any) -> Optional[bool]:
        """
        Evaluate CFN condition function's value
        Examples
        --------
        _evaluate_condition('Fn::Equals', ['test', 'prod']) -> False
        _evaluate_condition('Fn::Not', {'Fn::Equals': ['test', 'prod']}) -> True
        _evaluate_condition('Fn::Not', {'Fn::Equals': ['test', 'prod']}) -> True
        _evaluate_condition('Fn::Or', [{'Fn::Equals': ['parameter1name', 'parameter1name']}, {'Fn::Equals': ['parameter2name', 'wrongname']}] -> True
        _evaluate_condition('Condition', 'IsProduction'] -> True
        """

        if condition_fn == IntrinsicFunctions.CONDITION:
            return self._evaluate_condition_by_name(value)
        elif condition_fn == ConditionFunctions.EQUALS:
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str) and isinstance(value[1], str):
                return value[0] == value[1]
        elif condition_fn == ConditionFunctions.NOT:
            evaluated_condition = self._fetch_condition_dict(value)
            if isinstance(evaluated_condition, bool):
                return not evaluated_condition
        elif condition_fn == ConditionFunctions.AND and isinstance(value, list) and len(value) == 2:
            operand1 = self._fetch_condition_dict(value[0])
            operand2 = self._fetch_condition_dict(value[1])
            if isinstance(operand1, bool) and isinstance(operand2, bool):
                return operand1 and operand2
        elif condition_fn == ConditionFunctions.OR and isinstance(value, list) and len(value) == 2:
            operand1 = self._fetch_condition_dict(value[0])
            operand2 = self._fetch_condition_dict(value[1])
            if isinstance(operand1, bool) and isinstance(operand2, bool):
                return operand1 or operand2
        return None  # failed to evaluate the condition

    def _fetch_condition_dict(self, condition_dict: Dict[str, Any]) -> Optional[bool]:
        """
        Evaluate a condition dict of fn and value. This method basically receives a complex parameter which is a dict of
        a CFN fn and its value to evaluate, extracts them and calls _evaluate_condition for evaluation
        Examples
        --------
        _fetch_condition_operand_value({'Fn::Equals': ['parameter1name', 'parameter1name']}) -> True
        _fetch_condition_operand_value({'Fn::Equals': ['parameter1name', 'wrongname'], '__startline__': 144, '__endline__': 151}) -> False
        _fetch_condition_operand_value({'Condition': 'IsProduction', '__startline__': 109, '__endline__': 111}) -> True
        _fetch_condition_operand_value({'Condition': 'IsDevelop'}] -> False
        """

        if isinstance(condition_dict, dict):
            inner_condition, inner_value = next(
                ((current_condition_function, condition_dict[current_condition_function])
                 for current_condition_function in self.CONDITIONS_EVALUATED_FUNCTIONS
                 if current_condition_function in condition_dict),
                (None, None))
            if inner_condition and inner_value:
                return self._evaluate_condition(inner_condition, inner_value)
        return None

    @staticmethod
    def _evaluate_findinmap_connection(
        value: Any, dest_vertex_attributes: Dict[str, Any]
    ) -> tuple[str | None, str | None]:
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
    def _evaluate_getatt_connection(
        value: Any, dest_vertex_attributes: Dict[str, Any]
    ) -> tuple[str | None, str | None]:
        # value = [ "logicalNameOfResource", "attributeName" ]
        try:
            if isinstance(value, list) and len(value) == 2:
                resource_name = value[0]
                attribute_at_dest = value[1]
                dest_name = dest_vertex_attributes[CustomAttributes.BLOCK_NAME].split('.')[-1]
                evaluated_value = dest_vertex_attributes.get(
                    attribute_at_dest)  # we extract only build time atts, not runtime

                if evaluated_value and \
                        all(isinstance(element, str) for element in value) and \
                        resource_name == dest_name and \
                        dest_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.RESOURCE:
                    return str(evaluated_value), attribute_at_dest
        except TypeError as e:
            logging.debug(f"unable to _evaluate_getatt_connection: {e}")

        return None, None

    def _evaluate_sub_connection(
        self, value: Any, dest_vertex_attributes: Dict[str, Any]
    ) -> tuple[str | None, str | None]:
        if isinstance(value, (list, dict)):
            # TODO: Render values of list/dict types
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

    def _evaluate_if_connection(
        self, value: List[str], condition_vertex_attributes: Dict[str, Any]
    ) -> tuple[str | None, str | None]:
        """
        Evaluate a Condition Function IF.
        This method receives 2 parameters:
         value: a value to evaluate, e.g. [ConditionName, OperandIfTrue, OperandIfFalse]
         condition_vertex_attributes: the attributes of the ConditionName vertex
        The response is composed of the evaluated value and the hierarchy in case of nested Fn:Ifs functions,
        so later we can check if it used to be a Parameter of a literal string and so update the breadcrumbs
        Examples
        --------
        _fetch_condition_operand_value(['CreateProdResources', 'c1.xlarge', 'm1.large'], {...CreateProdResources vertex attributes...}) -> c1.xlarge if CreateProdResources is true, otherwise m1.large
        _fetch_condition_operand_value(['CreateProdResources', 'c1.xlarge', {'Fn::If': ['CreateDevResources', 'm1.large', 'm1.small']}]) -> If CreateProdResoruces if false & CreateDevResources if true then m1.large
        """

        evaluated_condition, evaluated_value, evaluated_value_hierarchy = (None, None, None)
        try:
            condition_name = value[0]
            operand_if_true = value[1]
            operand_if_false = value[2]
        except KeyError:
            logging.info(f'Unexpected input for cfn if evaluation: {value}. '
                         f'Template: {condition_vertex_attributes[CustomAttributes.FILE_PATH]}'
                         f'Block: {condition_vertex_attributes[CustomAttributes.BLOCK_NAME]}')
            return evaluated_value, evaluated_value_hierarchy

        # First, we evaluate the ConditionName
        if isinstance(condition_name, str) and\
                condition_name == condition_vertex_attributes.get(CustomAttributes.BLOCK_NAME) and \
                condition_vertex_attributes.get(CustomAttributes.BLOCK_TYPE) == BlockType.CONDITIONS:
            evaluated_condition = self._evaluate_condition_by_name(condition_name)

        # After we evaluate ConditionName, we fetch OperandIfTrue or OperandIfFalse (according to the result)
        if isinstance(evaluated_condition, bool):
            (operand_index, operand_to_eval) = (1, operand_if_true) if evaluated_condition else (2, operand_if_false)

            if isinstance(operand_to_eval, str):
                # The operand is a simple string
                evaluated_value = operand_to_eval
                evaluated_value_hierarchy = str(operand_index)
            elif isinstance(operand_to_eval, dict):
                if ConditionFunctions.IF in operand_to_eval:
                    # The operand is {'Fn::If': new value to evaluate}
                    condition_to_eval = operand_to_eval[ConditionFunctions.IF]
                    if isinstance(condition_to_eval, list) and isinstance(condition_to_eval[0], str):
                        condition_vertex_attributes = self._fetch_vertex_attributes(condition_to_eval[0], BlockType.CONDITIONS)
                        evaluated_value, evaluated_value_operand_index = self._evaluate_if_connection(condition_to_eval, condition_vertex_attributes)
                        evaluated_value_hierarchy = f'{operand_index}.{ConditionFunctions.IF}.{evaluated_value_operand_index}'
                elif not any([op for op in self.CONDITIONS_EVALUATED_FUNCTIONS if op in operand_to_eval]):
                    # The operand is a dict without any further actions to perform
                    evaluated_value = operand_to_eval

        return evaluated_value, evaluated_value_hierarchy

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
        vertices_block_name_map = pickle_deepcopy(self.local_graph.vertices_block_name_map)
        resources_blocks_name_map = vertices_block_name_map[BlockType.RESOURCE]

        updated_resources_blocks_name_map = {}
        for resource_name, blocks_list in resources_blocks_name_map.items():
            shortened_resource_name = resource_name.split('.')[
                -1]  # Trims AWS::X::Y.ResourceName and leaves us with ResoruceName
            updated_resources_blocks_name_map[shortened_resource_name] = blocks_list
        vertices_block_name_map[BlockType.RESOURCE] = updated_resources_blocks_name_map
        return vertices_block_name_map

    def _handle_dependson_condition_connections(self, edge: Edge, origin_vertex: CloudformationBlock) -> None:
        if edge.label == IntrinsicFunctions.CONDITION:
            dest_vertex_attributes = self.local_graph.get_vertex_attributes_by_index(edge.dest)
            evaluated_condition = self._evaluate_condition_by_vertex_attributes(dest_vertex_attributes)
            if isinstance(evaluated_condition, bool):
                # evaluated the condition successfully, add the result to the origin vertex
                origin_vertex.condition = evaluated_condition

    def _handle_edge_list_evaluation_functions(self, edge_list: List[Edge], origin_vertex: Block,
                                               val_to_eval: Dict[str, Any]) -> None:
        # Ref, GetAtt, FindInMap, If, Sub connections
        cfn_evaluation_function = next((
            curr_evaluation_function
            for curr_evaluation_function in self.EDGE_EVALUATION_CFN_FUNCTIONS
            if curr_evaluation_function in val_to_eval
        ), None)

        if cfn_evaluation_function:

            evaluated_edges: "list[_EvaluatedEdge]" = []
            for edge in edge_list:
                dest_vertex_attributes = self.local_graph.get_vertex_attributes_by_index(edge.dest)
                try:
                    (evaluated_value, changed_origin_id, attribute_at_dest) = self._evaluate_cfn_function(
                        edge, origin_vertex, cfn_evaluation_function, val_to_eval, dest_vertex_attributes)
                except KeyError:
                    logging.info(f'Failed to evalue cfn function. val_to_eval: {val_to_eval}')
                    continue

                if evaluated_value:
                    # succeeded to evaluate an edge
                    val_to_eval[cfn_evaluation_function] = evaluated_value
                    evaluated_edges.append({
                        'vertex_index': edge.origin,
                        'attribute_key': edge.label,
                        'attribute_value': evaluated_value,
                        'change_origin_id': changed_origin_id,
                        'attribute_at_dest': attribute_at_dest
                    })
                else:
                    # failed to evaluate an edge
                    break

            if len(evaluated_edges) == len(edge_list):
                # succeeded in evaluation all of the edges
                for evaluated_edge in evaluated_edges:
                    self.local_graph.update_vertex_attribute(
                        vertex_index=evaluated_edge['vertex_index'],
                        attribute_key=evaluated_edge['attribute_key'],
                        attribute_value=evaluated_edge['attribute_value'],
                        change_origin_id=evaluated_edge['change_origin_id'],
                        attribute_at_dest=evaluated_edge['attribute_at_dest']
                    )

    def _evaluate_cfn_function(
        self,
        edge: Edge,
        origin_vertex: Block,
        cfn_evaluation_function: str,
        val_to_eval: dict[str, Any],
        dest_vertex_attributes: dict[str, Any],
    ) -> tuple[str | None, int | None, str | None]:
        (evaluated_value, changed_origin_id, attribute_at_dest) = (None, None, None)

        if cfn_evaluation_function == ConditionFunctions.IF:
            # We evaluate Fn::IF differently from Ref, GetAtt, FindInMap, Sub
            evaluated_value, evaluated_value_hierarchy = self._evaluate_if_connection(
                val_to_eval[ConditionFunctions.IF], dest_vertex_attributes)
            if evaluated_value and evaluated_value_hierarchy:
                evaluated_value_hierarchy = f'{edge.label}.{ConditionFunctions.IF}.{evaluated_value_hierarchy}'
                changed_attribute = origin_vertex.changed_attributes.get(evaluated_value_hierarchy, None)
                (attribute_at_dest, changed_origin_id) = \
                    (changed_attribute[0].attribute_key, changed_attribute[0].vertex_id)\
                    if isinstance(changed_attribute, list) and len(changed_attribute) == 1\
                    else (None, None)
        else:
            # Ref, GetAtt, FindInMap, Sub evaluation
            evaluated_value, attribute_at_dest = self.edge_evaluation_methods[cfn_evaluation_function](
                val_to_eval[cfn_evaluation_function], dest_vertex_attributes)
            changed_origin_id = edge.dest

        return evaluated_value, changed_origin_id, attribute_at_dest

    def evaluate_non_rendered_values(self) -> None:

        for vertex in self.local_graph.vertices:
            vertex_attributes = pickle_deepcopy(vertex.attributes)
            for attr_key, attr_value in vertex_attributes.items():
                self._handle_sub_with_pseudo_param(attr_key, attr_value, vertex)

    @staticmethod
    def _handle_sub_with_pseudo_param(attr_key: str, attr_value: Any, vertex: CloudformationBlock) -> None:
        """
        Pseudo Parameter in CFN is a parameter which is dynamically available (see reference).
        As we do not render it on buildtime, we want to handle this case by keeping the reference itself without the
        value, so we can at least build a semi-full resource.
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/pseudo-parameter-reference.html
        """
        if isinstance(attr_value, dict) and IntrinsicFunctions.SUB in attr_value:
            inner_value = attr_value[IntrinsicFunctions.SUB]
            is_pseudo_param_in_value = any([p.value for p in PseudoParameters if p.value in inner_value])
            if isinstance(inner_value, (str, StrNode)):
                try:
                    inner_value = json.loads(inner_value)
                except Exception as e:
                    logging.debug(f"[Cloudformation_evaluate_non_rendered_values]- "
                                  f"Inner_value - {inner_value} is not a valid json. "
                                  f"Full exception - {str(e)}")
            if is_pseudo_param_in_value:
                vertex.update_attribute(
                    attribute_key=attr_key, attribute_value=inner_value, change_origin_id=None,
                    previous_breadcrumbs=[], attribute_at_dest=None
                )
