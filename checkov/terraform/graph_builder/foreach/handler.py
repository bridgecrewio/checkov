from checkov.terraform.graph_builder.foreach.module_handler import ForeachModuleHandler
from checkov.terraform.graph_builder.foreach.resource_handler import ForeachResourceHandler
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachHandler:
    def __init__(self, local_graph: TerraformLocalGraph):
        self._resource_handler = ForeachResourceHandler(local_graph)
        self._module_handler = ForeachModuleHandler(local_graph)

    def handle(self, foreach_blocks: dict[str, list[int]]) -> None:
        self._module_handler.handle(foreach_blocks.get(BlockType.MODULE))
        self._resource_handler.handle(foreach_blocks.get(BlockType.RESOURCE))
