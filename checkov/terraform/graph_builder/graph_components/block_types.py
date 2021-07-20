from checkov.common.graph.graph_builder.graph_components.block_types import BlockType as CommonBlockType
from dataclasses import dataclass


@dataclass
class BlockType(CommonBlockType):
    DATA = "data"
    LOCALS = "locals"
    MODULE = "module"
    OUTPUT = "output"
    PROVIDER = "provider"
    TERRAFORM = "terraform"
    TF_VARIABLE = "tfvar"
    VARIABLE = "variable"
    CUSTOM = "custom"
