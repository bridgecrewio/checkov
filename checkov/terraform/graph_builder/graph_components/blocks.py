import os
from typing import Union, Dict, Any, List, Optional, Set

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.variable_rendering.breadcrumb_metadata import BreadcrumbMetadata
from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.utils import remove_module_dependency_in_path


class TerraformBlock(Block):
    def __init__(self, name: str, config: Dict[str, Any], path: str, block_type: BlockType, attributes: Dict[str, Any],
                 id: str = "", source: str = "") -> None:
        """
            :param name: unique name given to the terraform block, for example: 'aws_vpc.example_name'
            :param config: the section in tf_definitions that belong to this block
            :param path: the file location of the block
            :param block_type: BlockType
            :param attributes: dictionary of the block's original attributes in the terraform file
        """
        super(TerraformBlock, self).__init__(name, config, path, block_type, attributes, id, source)
        self.module_dependency = ""
        self.module_dependency_num = ""
        if path:
            self.path, module_dependency, num = remove_module_dependency_in_path(path)
            self.path = os.path.realpath(self.path)
            if module_dependency:
                self.module_dependency = module_dependency
                self.module_dependency_num = num
        if attributes.get(RESOLVED_MODULE_ENTRY_NAME):
            del attributes[RESOLVED_MODULE_ENTRY_NAME]
        self.attributes = attributes
        self.module_connections: Dict[str, List[int]] = {}
        self.source_module: Set[int] = set()

    def add_module_connection(self, attribute_key: str, vertex_id: int) -> None:
        self.module_connections.setdefault(attribute_key, []).append(vertex_id)

    def find_attribute(self, attribute: Optional[Union[str, List[str]]]) -> Optional[str]:
        """
        :param attribute: key to search in self.attributes
        The function searches for  attribute in self.attribute. It might not exist if the block is variable or output,
        or its search path might be different if its a resource.
        :return: the actual attribute key or None
        """
        if not attribute:
            return None

        if self.attributes.get(attribute[0]):
            return attribute[0]

        if self.block_type == BlockType.VARIABLE:
            return "default" if self.attributes.get("default") else None

        if self.block_type == BlockType.OUTPUT:
            return "value" if self.attributes.get("value") else None

        if self.block_type == BlockType.RESOURCE and len(attribute) > 1:
            # handle cases where attribute_at_dest == ['aws_s3_bucket.template_bucket', 'acl']
            if self.name == attribute[0] and self.attributes.get(attribute[1]):
                return attribute[1]

        return None

    def update_attribute(
        self, attribute_key: str, attribute_value: Any, change_origin_id: int,
            previous_breadcrumbs: List[BreadcrumbMetadata], attribute_at_dest: str
    ) -> None:
        self.update_inner_attribute(attribute_key, self.attributes, attribute_value)
        super().update_attribute(attribute_key, attribute_value, change_origin_id, previous_breadcrumbs, attribute_at_dest)

    def update_inner_attribute(
        self, attribute_key: str, nested_attributes: Union[List[Any], Dict[str, Any]], value_to_update: Any
    ) -> None:
        split_key = attribute_key.split(".")
        i = 1
        curr_key = ".".join(split_key[0:i])
        if isinstance(nested_attributes, list):
            if curr_key.isnumeric():
                curr_key_int = int(curr_key)
                if curr_key_int < len(nested_attributes):
                    if not isinstance(nested_attributes[curr_key_int], dict):
                        nested_attributes[curr_key_int] = value_to_update
                    else:
                        self.update_inner_attribute(
                            ".".join(split_key[i:]), nested_attributes[curr_key_int], value_to_update
                        )
            else:
                for inner in nested_attributes:
                    self.update_inner_attribute(curr_key, inner, value_to_update)
        elif isinstance(nested_attributes, dict):
            while curr_key not in nested_attributes and i <= len(split_key):
                i += 1
                curr_key = ".".join(split_key[0:i])
            if attribute_key in nested_attributes.keys():
                nested_attributes[attribute_key] = value_to_update
            if len(split_key) == 1 and len(curr_key) > 0:
                nested_attributes[curr_key] = value_to_update
            elif curr_key in nested_attributes.keys():
                self.update_inner_attribute(".".join(split_key[i:]), nested_attributes[curr_key], value_to_update)

    @classmethod
    def get_inner_attributes(
        cls,
        attribute_key: str,
        attribute_value: Union[str, List[str], Dict[str, Any]],
        strip_list: bool = True
    ) -> Dict[str, Any]:
        if strip_list and isinstance(attribute_value, list) and len(attribute_value) == 1:
            attribute_value = attribute_value[0]

        return super().get_inner_attributes(
            attribute_key=attribute_key,
            attribute_value=attribute_value,
        )
