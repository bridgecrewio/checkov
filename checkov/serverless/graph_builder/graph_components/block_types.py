from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType as CommonBlockType


@dataclass
class BlockType(CommonBlockType):
    PROVIDER: Literal["provider"] = "provider"
    FUNCTIONS: Literal["functions"] = "functions"
