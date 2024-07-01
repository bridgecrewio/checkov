from __future__ import annotations

import typing

from checkov.terraform.graph_builder.foreach.data_handler import ForeachDataHandler
from checkov.terraform.graph_builder.foreach.module_handler import ForeachModuleHandler
from checkov.terraform.graph_builder.foreach.resource_handler import ForeachResourceHandler
from checkov.terraform.graph_builder.graph_components.block_types import BlockType

if typing.TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachBuilder:
    def __init__(self, local_graph: TerraformLocalGraph):
        self._resource_handler = ForeachResourceHandler(local_graph)
        self._module_handler = ForeachModuleHandler(local_graph)
        self._data_handler = ForeachDataHandler(local_graph)

    def handle(self, foreach_blocks: dict[str, list[int]]) -> None:
        """
        First Data blocks that Modules can inherit from are handled.
        Second, Module blocks are handled.
        Last Resource blocks that can be duplicate by the Modules rendering.
        """
        if self._data_handler.local_graph.enable_datas_foreach_handling:
            if foreach_blocks.get(BlockType.DATA):
                self._data_handler.handle(foreach_blocks[BlockType.DATA])
                self._data_handler.local_graph._arrange_graph_data()
                self._data_handler.local_graph._build_edges()
        if self._module_handler.local_graph.enable_modules_foreach_handling:
            if foreach_blocks.get(BlockType.MODULE):
                self._module_handler.handle(foreach_blocks[BlockType.MODULE])
        if self._module_handler.local_graph.enable_foreach_handling:
            self._resource_handler.handle(foreach_blocks.get(BlockType.RESOURCE, []))
