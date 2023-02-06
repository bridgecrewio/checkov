from __future__ import annotations

import logging
import re
from typing import Any, Optional, TypeVar

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer
import checkov.terraform.graph_builder.local_graph as l_graph
from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import evaluate_terraform

FOREACH_STRING = 'for_each'
COUNT_STRING = 'count'
REFERENCES_VALUES = r"(var|module|local)\."
FOR_EACH_BLOCK_TYPE = TypeVar("FOR_EACH_BLOCK_TYPE", bound="dict[int, Optional[list[str] | dict[str, Any] | int]]")


class ForeachHandler(object):
    def __init__(self, local_graph: l_graph.TerraformLocalGraph) -> None:
        self.local_graph = local_graph

    def handle_foreach_rendering(self, foreach_blocks: dict[str, list[int]]) -> None:
        # handle_foreach_rendering_for_module(foreach_blocks.get(BlockType.MODULE))
        self._handle_foreach_rendering_for_resource(foreach_blocks.get(BlockType.RESOURCE))

    def _handle_foreach_rendering_for_resource(self, resources_blocks: list[int]) -> None:
        block_index_to_statement = self._get_statements(resources_blocks)
        self._create_new_foreach_resources(block_index_to_statement)

    def _get_statements(self, resources_blocks: list[int]) -> FOR_EACH_BLOCK_TYPE:
        block_index_to_statement: FOR_EACH_BLOCK_TYPE = {}
        for block_index in resources_blocks:
            foreach_statement = self._get_static_foreach_statement(block_index)
            block_index_to_statement[block_index] = foreach_statement
        blocks_to_render = [block_idx for block_idx, statement in block_index_to_statement.items() if statement is None]
        rendered_statements = self._handle_dynamic_statement(blocks_to_render)
        block_index_to_statement.update(rendered_statements)
        return block_index_to_statement

    def _get_static_foreach_statement(self, block_index: int) -> Optional[list[str] | dict[str, Any]]:
        attributes = self.local_graph.vertices[block_index].attributes
        if not attributes.get(FOREACH_STRING) and not attributes.get(COUNT_STRING):
            return
        try:
            if self._is_static_statement(block_index):
                return self._handle_static_statement(block_index)
            else:
                return None
        except Exception as e:
            logging.info(f"Cant get foreach statement for block: {self.local_graph.vertices[block_index]}, error: {str(e)}")
            return None

    def _is_static_foreach_statement(self, statement: list[str] | dict[str, Any]) -> bool:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        if isinstance(statement, str) and re.search(REFERENCES_VALUES, statement):
            return False
        if isinstance(statement, (list, dict)) and any([re.search(REFERENCES_VALUES, s) for s in statement]):
            return False
        return True

    def _is_static_count_statement(self, statement: list[str] | int) -> bool:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        if isinstance(statement, int):
            return True
        if isinstance(statement, str) and not re.search(REFERENCES_VALUES, statement):
            return True
        return False

    def _is_static_statement(self, block_index: int, sub_graph: Optional[l_graph.TerraformLocalGraph] = None) -> bool:
        """
        foreach statement can be list/map of strings or map, if its string we need to render it for sure.
        """
        block = self.local_graph.vertices[block_index] if not sub_graph else sub_graph.vertices[block_index]
        foreach_statement = evaluate_terraform(block.attributes.get(FOREACH_STRING))
        count_statement = evaluate_terraform(block.attributes.get(COUNT_STRING))
        if foreach_statement:
            return self._is_static_foreach_statement(foreach_statement)
        if count_statement:
            return self._is_static_count_statement(count_statement)
        return False

    @staticmethod
    def extract_from_list(val: list[str] | list[int]) -> list[str] | list[int] | int | str:
        return val[0] if len(val) == 1 and isinstance(val[0], (str, int)) else val

    def _handle_static_foreach_statement(self, statement: list[str] | dict[str, Any]) -> Optional[list[str] | dict[str, Any]]:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        evaluated_statement = evaluate_terraform(statement)
        if isinstance(evaluated_statement, set):
            evaluated_statement = list(evaluated_statement)
        if isinstance(evaluated_statement, (dict, list)) and all(isinstance(val, str) for val in evaluated_statement):
            return evaluated_statement
        return

    def _handle_static_count_statement(self, statement: list[str] | int) -> Optional[int]:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        evaluated_statement = evaluate_terraform(statement)
        if isinstance(evaluated_statement, int):
            return evaluated_statement
        return

    def _handle_static_statement(self, block_index: int, sub_graph: Optional[l_graph.TerraformLocalGraph] = None) -> Optional[list[str] | dict[str, Any] | int]:
        attrs = self.local_graph.vertices[block_index].attributes if not sub_graph else sub_graph.vertices[block_index].attributes
        foreach_statement = attrs.get(FOREACH_STRING)
        count_statement = attrs.get(COUNT_STRING)
        if foreach_statement:
            return self._handle_static_foreach_statement(foreach_statement)
        if count_statement:
            return self._handle_static_count_statement(count_statement)
        return

    def _handle_dynamic_statement(self, blocks_to_render: list[int]) -> FOR_EACH_BLOCK_TYPE:
        rendered_statements_by_idx: FOR_EACH_BLOCK_TYPE = {}
        sub_graph = self._build_sub_graph(blocks_to_render)
        self._render_sub_graph(sub_graph, blocks_to_render)
        for block_idx in blocks_to_render:
            if not self._is_static_statement(block_idx, sub_graph):
                rendered_statements_by_idx[block_idx] = None
            else:
                rendered_statements_by_idx[block_idx] = self._handle_static_statement(block_idx, sub_graph)
        return rendered_statements_by_idx

    @staticmethod
    def _render_sub_graph(sub_graph: l_graph.TerraformLocalGraph, blocks_to_render: list[int]) -> None:
        renderer = TerraformVariableRenderer(sub_graph)
        renderer.vertices_index_to_render = blocks_to_render
        renderer.render_variables_from_local_graph()

    def _build_sub_graph(self, blocks_to_render: list[int]) -> l_graph.TerraformLocalGraph:
        sub_graph = l_graph.TerraformLocalGraph(self.local_graph.module)
        sub_graph.vertices = [{}] * len(self.local_graph.vertices)
        for i, block in enumerate(self.local_graph.vertices):
            if not (block.block_type == BlockType.RESOURCE and i not in blocks_to_render):
                sub_graph.vertices[i] = block  # type: ignore
        sub_graph.edges = [
            edge for edge in self.local_graph.edges if (sub_graph.vertices[edge.dest] and sub_graph.vertices[edge.origin])
        ]
        sub_graph.in_edges = self.local_graph.in_edges
        sub_graph.out_edges = self.local_graph.out_edges
        return sub_graph

    def _create_new_foreach_resources(self, block_index_to_statement: FOR_EACH_BLOCK_TYPE) -> None:
        pass
