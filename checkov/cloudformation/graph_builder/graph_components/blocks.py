from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.variable_rendering.breadcrumb_metadata import BreadcrumbMetadata


class CloudformationBlock(Block):
    __slots__ = ("condition", "metadata")

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        path: str,
        block_type: str,
        attributes: Dict[str, Any],
        id: str = "",
        source: str = "",
        condition: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
            :param name: unique name given to the terraform block, for example: 'aws_vpc.example_name'
            :param config: the section in tf_definitions that belong to this block
            :param path: the file location of the block
            :param block_type: str
            :param attributes: dictionary of the block's original attributes in the terraform file
        """
        super().__init__(name, config, path, block_type, attributes, id, source)
        self.condition = condition
        self.metadata = metadata

    def update_attribute(
        self, attribute_key: str,
        attribute_value: Any,
        change_origin_id: int,
        previous_breadcrumbs: List[BreadcrumbMetadata],
        attribute_at_dest: str,
        transform_step: bool = False,
    ) -> None:
        super().update_attribute(
            attribute_key=attribute_key,
            attribute_value=attribute_value,
            change_origin_id=change_origin_id,
            previous_breadcrumbs=previous_breadcrumbs,
            attribute_at_dest=attribute_at_dest,
            transform_step=transform_step,
        )

        attribute_key_parts = attribute_key.split(".")
        if attribute_key_parts:
            obj_to_update = self.attributes
            key_to_update = attribute_key_parts.pop()
            for i, key in enumerate(attribute_key_parts):
                if isinstance(obj_to_update, list):
                    key = int(key)
                if (isinstance(obj_to_update, dict) and key in obj_to_update) or \
                        (isinstance(obj_to_update, list) and isinstance(key, int) and 0 <= key < len(
                            obj_to_update)):
                    obj_to_update = obj_to_update[key]
                else:
                    attribute_key_parts.append(key_to_update)
                    key_to_update = ".".join(attribute_key_parts[i:])
                    break

            if isinstance(obj_to_update, list):
                key_to_update = int(key_to_update)
            if isinstance(obj_to_update, (dict, list)):
                obj_to_update[key_to_update] = attribute_value
            else:
                logging.info(f"Failed to update an attribute, values: {obj_to_update}, {key_to_update}, {attribute_value}")

    def update_inner_attribute(
        self, attribute_key: str, nested_attributes: list[Any] | dict[str, Any], value_to_update: Any
    ) -> None:
        # this overrides the parent method, which doesn't work as expected with CloudFormation
        pass

    @staticmethod
    def _should_add_previous_breadcrumbs(change_origin_id: Optional[int],
                                         previous_breadcrumbs: List[BreadcrumbMetadata],
                                         attribute_at_dest: Optional[str]):
        return (
            change_origin_id is not None
            and attribute_at_dest is not None
            and (not previous_breadcrumbs or previous_breadcrumbs[-1].vertex_id != change_origin_id)
        )

    @staticmethod
    def _should_set_changed_attributes(change_origin_id: Optional[int], attribute_at_dest: Optional[str]):
        return change_origin_id is not None and attribute_at_dest is not None