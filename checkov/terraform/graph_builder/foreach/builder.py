from __future__ import annotations

import typing

from checkov.terraform.graph_builder.foreach.module_handler import ForeachModuleHandler
from checkov.terraform.graph_builder.foreach.resource_handler import ForeachResourceHandler
from checkov.terraform.graph_builder.graph_components.block_types import BlockType

if typing.TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachBuilder:
    def __init__(self, local_graph: TerraformLocalGraph):
        self._resource_handler = ForeachResourceHandler(local_graph)
        self._module_handler = ForeachModuleHandler(local_graph)

    def handle(self, foreach_blocks: dict[str, list[int]]) -> None:
        if self._module_handler.local_graph.enable_modules_foreach_handling:
            if foreach_blocks.get(BlockType.MODULE):
                self._module_handler.handle(foreach_blocks[BlockType.MODULE])
                self._module_handler.local_graph._arrange_graph_data()
                self._module_handler.local_graph._build_edges()
        if self._module_handler.local_graph.enable_foreach_handling:
            self._resource_handler.handle(foreach_blocks.get(BlockType.RESOURCE, []))
