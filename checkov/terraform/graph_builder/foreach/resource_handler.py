from __future__ import annotations

from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.foreach.foreach_entity_handler import ForeachEntityHandler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachResourceHandler(ForeachEntityHandler):

    def __init__(self, local_graph: TerraformLocalGraph) -> None:
        super().__init__(local_graph, BlockType.RESOURCE)
