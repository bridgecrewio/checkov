from __future__ import annotations

import logging
from typing import Any, Optional, TYPE_CHECKING

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.env_vars_config import env_vars_config
from checkov.terraform.graph_builder.foreach.abstract_handler import ForeachAbstractHandler
from checkov.terraform.graph_builder.foreach.consts import FOR_EACH_BLOCK_TYPE, FOREACH_STRING, COUNT_STRING
from checkov.terraform.graph_builder.foreach.utils import append_virtual_resource
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock

if TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachEntityHandler(ForeachAbstractHandler):
    def __init__(self, local_graph: TerraformLocalGraph, block_type_to_handle: str) -> None:
        super().__init__(local_graph)
        self.block_type_to_handle = block_type_to_handle

    def handle(self, resources_blocks: list[int]) -> None:
        block_index_to_statement: FOR_EACH_BLOCK_TYPE = self._get_statements(resources_blocks)
        self._create_new_resources(block_index_to_statement)

    def _get_statements(self, resources_blocks: list[int]) -> FOR_EACH_BLOCK_TYPE:
        if not resources_blocks:
            return {}
        block_index_to_statement: FOR_EACH_BLOCK_TYPE = {}
        for block_index, block in enumerate(self.local_graph.vertices):
            if block.block_type != self.block_type_to_handle or not (
                    FOREACH_STRING in block.attributes or COUNT_STRING in block.attributes):
                continue
            foreach_statement = self._get_static_foreach_statement(block_index)
            block_index_to_statement[block_index] = foreach_statement
        blocks_to_render = [block_idx for block_idx, statement in block_index_to_statement.items() if statement is None]
        if blocks_to_render:
            rendered_statements: FOR_EACH_BLOCK_TYPE = self._handle_dynamic_statement(blocks_to_render)
            block_index_to_statement.update(rendered_statements)
        return block_index_to_statement

    def _get_static_foreach_statement(self, block_index: int) -> Optional[list[str] | dict[str, Any] | int]:
        attributes = self.local_graph.vertices[block_index].attributes
        if not attributes.get(FOREACH_STRING) and not attributes.get(COUNT_STRING):
            return None
        try:
            if self._is_static_statement(block_index):
                return self._handle_static_statement(block_index)
            else:
                return None
        except Exception as e:
            logging.info(
                f"Cannot get foreach statement for block: {self.local_graph.vertices[block_index]}, error: {str(e)}")
            return None

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

    def _create_new_resources_count(self, statement: int, block_idx: int) -> None:
        main_resource = self.local_graph.vertices[block_idx]
        virtual_resources_names: list[str] = []
        for i in range(statement):
            append_virtual_resource(self._create_new_resource(main_resource, i, resource_idx=block_idx, foreach_idx=i),
                                    virtual_resources_names)
        if env_vars_config.RAW_TF_IN_GRAPH_ENV:
            main_resource.config[CustomAttributes.VIRTUAL_RESOURCES] = virtual_resources_names
            self.local_graph.vertices.append(main_resource)

    def _create_new_foreach_resource(self, block_idx: int, foreach_idx: int, main_resource: TerraformBlock,
                                     new_key: int | str, new_value: int | str) -> str | None:
        return self._create_new_resource(main_resource, new_value, new_key=new_key, resource_idx=block_idx,
                                         foreach_idx=foreach_idx)

    def _create_new_resource(
            self,
            main_resource: TerraformBlock,
            new_value: int | str,
            resource_idx: int,
            foreach_idx: int,
            new_key: int | str | None = None,
    ) -> str | None:
        new_resource = pickle_deepcopy(main_resource)
        block_type, block_name = new_resource.name.split('.')
        key_to_val_changes = self._build_key_to_val_changes(main_resource, new_value, new_key)
        config_attrs = new_resource.config.get(block_type, {}).get(block_name, {})

        self._update_foreach_attrs(config_attrs, key_to_val_changes, new_resource)
        idx_to_change = new_key or new_value
        self._add_index_to_resource_block_properties(new_resource, idx_to_change)
        if foreach_idx == 0:
            self.local_graph.vertices[resource_idx] = new_resource
        else:
            self.local_graph.vertices.append(new_resource)

        if env_vars_config.RAW_TF_IN_GRAPH_ENV:
            return new_resource.name

        return None

    @staticmethod
    def _add_index_to_resource_block_properties(block: TerraformBlock, idx: str | int) -> None:
        block_type, block_name = block.name.split('.')
        idx_with_separator = ForeachEntityHandler._update_block_name_and_id(block, idx)
        if block.config.get(block_type) and block.config.get(block_type, {}).get(block_name):
            block.config[block_type][f"{block_name}[{idx_with_separator}]"] = block.config[block_type].pop(block_name)

    def _create_new_resources(self, block_index_to_statement: FOR_EACH_BLOCK_TYPE) -> None:
        for block_idx, statement in block_index_to_statement.items():
            if not statement:
                continue
            if isinstance(statement, int):
                self._create_new_resources_count(statement, block_idx)
            else:
                self._create_new_resources_foreach(statement, block_idx)
