from typing import Dict, Any

from checkov.common.graph.graph_builder.graph_components.blocks import Block


class CloudformationBlock(Block):
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        path: str,
        block_type: str,
        attributes: Dict[str, Any],
        id: str = "",
        source: str = "",
    ) -> None:
        """
            :param name: unique name given to the terraform block, for example: 'aws_vpc.example_name'
            :param config: the section in tf_definitions that belong to this block
            :param path: the file location of the block
            :param block_type: str
            :param attributes: dictionary of the block's original attributes in the terraform file
        """
        super().__init__(name, config, path, block_type, attributes, id, source)
