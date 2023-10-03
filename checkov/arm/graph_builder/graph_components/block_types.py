from dataclasses import dataclass
from typing import TYPE_CHECKING

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType as CommonBlockType

if TYPE_CHECKING:
    from typing_extensions import Literal


@dataclass
class BlockType(CommonBlockType):
    PARAMETER: 'Literal["parameter"]' = "parameter"
