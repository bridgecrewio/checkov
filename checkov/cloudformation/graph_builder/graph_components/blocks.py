from typing import Dict, Any, Optional, Union, List

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType


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

    def find_attribute(self, attribute: Optional[Union[str, List[str]]]) -> Optional[str]:
        """
        :param attribute: key to search in self.attributes
        The function searches for  attribute in self.attribute. It might not exist if the block is variable or output,
        or its search path might be different if its a resource.
        :return: the actual attribute key or None
        """
        if not attribute:
            return None

        if self.block_type == BlockType.PARAMETERS:
            return "Default" if self.attributes.get("Default") else None
        # else:
        #     print('here')
        #
        # if self.block_type == BlockType.OUTPUTS:
        #     return "value" if self.attributes.get("value") else None
        #
        # if self.block_type == BlockType.RESOURCE and len(attribute) > 1:
        #     # handle cases where attribute_at_dest == ['aws_s3_bucket.template_bucket', 'acl']
        #     if self.name == attribute[0] and self.attributes.get(attribute[1]):
        #         return attribute[1]

        return None
