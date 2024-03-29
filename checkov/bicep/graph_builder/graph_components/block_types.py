from dataclasses import dataclass
from typing import Literal

from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType as CommonBlockType

BlockTypeAlias: TypeAlias = Literal["targetScope", "param", "var", "resource", "module", "output"]


@dataclass
class BlockType(CommonBlockType):
    TARGET_SCOPE: Literal["targetScope"] = "targetScope"
    PARAM: Literal["param"] = "param"
    VAR: Literal["var"] = "var"
    MODULE: Literal["module"] = "module"
    OUTPUT: Literal["output"] = "output"
