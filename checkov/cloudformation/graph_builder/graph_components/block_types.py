from dataclasses import dataclass
from enum import Enum

from checkov.common.graph.graph_builder.graph_components.block_types import BlockType as CommonBlockType


@dataclass
class BlockType(CommonBlockType):
    METADATA = "metadata"
    PARAMETER = "parameters"
    RULE = "rules"
    MAPPING = "mappings"
    CONDITION = "conditions"
    TRANSFORM = "transform"
    OUTPUT = "outputs"


class CloudformationTemplateSections(str, Enum):
    RESOURCES = "Resources"
    METADATA = "Metadata"
    PARAMETERS = "Parameters"
    RULES = "Rules"
    MAPPINGS = "Mappings"
    CONDITIONS = "Conditions"
    TRANSFORM = "Transform"
    OUTPUTS = "Outputs"
