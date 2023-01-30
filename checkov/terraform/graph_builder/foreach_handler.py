from __future__ import annotations

import logging
import re
from typing import Any, Optional, TYPE_CHECKING

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
if TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import evaluate_terraform


class ForeachHandler:
    def __init__(self, local_graph: TerraformLocalGraph) -> None:
        self.local_graph = local_graph

    def handle_foreach_rendering(self, foreach_blocks: dict[str, list[int]]):
        # handle_foreach_rendering_for_module(foreach_blocks.get(BlockType.MODULE))
        self._handle_foreach_rendering_for_resource(foreach_blocks.get(BlockType.RESOURCE))

    def _handle_foreach_rendering_for_resource(self, resources_blocks: list[int]):
        # old_resources_to_delete_edges: list[TerraformBlock] = []
        # new_resource_to_create_edges: list[TerraformBlock] = []
        for i in resources_blocks:
            foreach_statement = self._get_foreach_statement(i)
            # empty foreach_statement -> leave the main resource
            if foreach_statement is None:
                continue
            # new_resources = self._create_new_foreach_resources(i, foreach_statement)
            # old_resources_to_delete_edges.append(tf_block)
            # new_resource_to_create_edges.extend(create_new_foreach_resources(tf_block))
        # delete_edges_from_old_resource(old_resources_to_delete_edges)
        # create_edges_for_new_foreach_resources(new_resource_to_create_edges)

    def _get_foreach_statement(self, block_index: int) -> Optional[list[str] | dict[str, Any]]:
        try:
            if self._is_static_statement(block_index):
                return evaluate_terraform(self.extract_str_from_list(self.local_graph.vertices[block_index].attributes.get('for_each')))
            else:
                # TODO implement foreach statement rendering
                return None
        except Exception as e:
            logging.info(f"Cant get foreach statement for block: {self.local_graph.vertices[block_index]}, error: {str(e)}")
            return None

    def _is_static_statement(self, block_index: int) -> bool:
        """
        foreach statement can be list/map of strings or map, if its string we need to render it for sure.
        """
        block = self.local_graph.vertices[block_index]
        foreach_statement = evaluate_terraform(block.attributes.get("for_each", [""]))
        if isinstance(foreach_statement, list) and len(foreach_statement) == 1:
            foreach_statement = foreach_statement[0]
        return not (isinstance(foreach_statement, str) and re.search(r"(var|module|local)\.", foreach_statement))

    @staticmethod
    def extract_str_from_list(val: list[str] | str | dict[str, Any]) -> list[str] | str | dict[str, Any]:
        if isinstance(val, list) and len(val) == 1 and isinstance(val[0], str):
            return val[0]
        return val

    def _create_new_foreach_resources(self, block_index: int, foreach_statement: list[str] | dict[str, Any]) -> list[int]:
        raise NotImplementedError

    def _delete_edges_from_old_resource(self, block: list[TerraformBlock]):
        raise NotImplementedError

    def _create_edges_for_new_foreach_resources(self, blocks: list[TerraformBlock]):
        raise NotImplementedError
