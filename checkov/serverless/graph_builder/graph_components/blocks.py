from __future__ import annotations

from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_builder.graph_components.blocks import Block


class ServerlessBlock(Block):
    def __init__(
        self,
        name: str,
        config: dict[str, any],
        path: str,
        block_type: str,
        attributes: dict[str, any],
        id: str = "",
    ) -> None:
        super().__init__(name, config, path, block_type, attributes, id, GraphSource.SERVERLESS)
