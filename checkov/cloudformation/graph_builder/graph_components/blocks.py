from typing import Dict, Any

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType


class CloudformationBlock(Block):
    def __init__(self, name: str, config: Dict[str, Any], path: str, block_type: BlockType, attributes: Dict[str, Any],
                 id: str = "", source: str = "") -> None:
        """
            :param name: unique name given to the terraform block, for example: 'aws_vpc.example_name'
            :param config: the section in tf_definitions that belong to this block
            :param path: the file location of the block
            :param block_type: BlockType
            :param attributes: dictionary of the block's original attributes in the terraform file
        """
        super(CloudformationBlock, self).__init__(name, config, path, block_type, attributes, id, source)
