from typing import List, Dict, Any

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.variable_rendering.breadcrumb_metadata import BreadcrumbMetadata


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

    def update_attribute(
        self, attribute_key: str, attribute_value: Any, change_origin_id: int,
            previous_breadcrumbs: List[BreadcrumbMetadata], attribute_at_dest: str
    ) -> None:
        super().update_attribute(attribute_key, attribute_value, change_origin_id, previous_breadcrumbs, attribute_at_dest)

        attribute_key_parts = attribute_key.split(".")
        if len(attribute_key_parts) > 1:
            obj_to_update = self.attributes
            for key in attribute_key_parts[:-1]:
                if isinstance(obj_to_update, list):
                    key = int(key)
                obj_to_update = obj_to_update[key]

            key_to_update = attribute_key_parts[-1]
            if isinstance(obj_to_update, list):
                key_to_update = int(key_to_update)
            obj_to_update[key_to_update] = attribute_value
