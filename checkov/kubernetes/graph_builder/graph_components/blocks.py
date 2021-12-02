from typing import Dict, Any

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType


class KubernetesBlock(Block):
    def __init__(
            self,
            block_name: str,
            resource_type: str,
            config: Dict[str, Any],
            path: str,
            attributes: Dict[str, Any],
    ) -> None:
        super().__init__(block_name, config, path, BlockType.RESOURCE, attributes, block_name, 'Kubernetes')
