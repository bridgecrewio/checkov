from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType


@dataclass
class KubernetesSelector:
    match_labels: Dict[str, Any] | None


@dataclass
class KubernetesBlockMetadata:
    selector: KubernetesSelector
    labels: Dict[str, Any]
    name: str


class KubernetesBlock(Block):
    def __init__(
            self,
            block_name: str,
            resource_type: str,
            config: Dict[str, Any],
            path: str,
            attributes: Dict[str, Any],
            metadata: KubernetesBlockMetadata | None
    ) -> None:
        super().__init__(block_name, config, path, BlockType.RESOURCE, attributes, block_name, 'Kubernetes')
        self.metadata = metadata
        self.resource_type = resource_type
