from dataclasses import dataclass

from typing_extensions import Literal

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType as CommonBlockType


@dataclass
class BlockType(CommonBlockType):
    TARGET_SCOPE: Literal["targetScope"] = "targetScope"
    PARAM: Literal["param"] = "param"
    VAR: Literal["var"] = "var"
    MODULE: Literal["module"] = "module"
    OUTPUT: Literal["output"] = "output"
