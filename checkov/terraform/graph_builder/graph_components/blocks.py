from __future__ import annotations

import os
from typing import Union, Dict, Any, List, Optional, Set, TYPE_CHECKING
import dpath
import re

from checkov.common.runners.base_runner import strtobool
from checkov.terraform.graph_builder.utils import INTERPOLATION_EXPR
from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.utils import remove_module_dependency_in_path

if TYPE_CHECKING:
    from checkov.terraform import TFModule, TFDefinitionKey


class TerraformBlock(Block):
    __slots__ = (
        "module_connections",
        "module_dependency",
        "module_dependency_num",
        "source_module",
        "has_dynamic_block",
        "dynamic_attributes",
        "foreach_attrs",
        "source_module_object",
        "for_each_index"
    )

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        path: str | TFDefinitionKey,
        block_type: str,
        attributes: Dict[str, Any],
        id: str = "",
        source: str = "",
        has_dynamic_block: bool = False,
        dynamic_attributes: dict[str, Any] | None = None,
    ) -> None:
        """
            :param name: unique name given to the terraform block, for example: 'aws_vpc.example_name'
            :param config: the section in tf_definitions that belong to this block
            :param path: the file location of the block
            :param block_type: BlockType
            :param attributes: dictionary of the block's original attributes in the terraform file
        """
        super().__init__(
            name=name,
            config=config,
            path=path,  # type:ignore[arg-type]  # Block class would need to be a Generic type to make this pass
            block_type=str(block_type),
            attributes=attributes,
            id=id,
            source=source,
            has_dynamic_block=has_dynamic_block,
            dynamic_attributes=dynamic_attributes,
        )
        self.module_dependency: str | None = ""
        self.module_dependency_num: str | None = ""
        if path:
            if strtobool(os.getenv('CHECKOV_ENABLE_NESTED_MODULES', 'True')):
                self.path = path  # type:ignore[assignment]  # Block class would need to be a Generic type to make this pass
            else:
                self.path, module_dependency, num = remove_module_dependency_in_path(path)  # type:ignore[arg-type]
                self.path = os.path.realpath(self.path)
                if module_dependency:
                    self.module_dependency = module_dependency
                    self.module_dependency_num = num
        if attributes.get(RESOLVED_MODULE_ENTRY_NAME):
            del attributes[RESOLVED_MODULE_ENTRY_NAME]
        self.attributes = attributes
        self.module_connections: Dict[str, List[int]] = {}
        self.source_module: Set[int] = set()
        self.has_dynamic_block = has_dynamic_block
        if strtobool(os.getenv('CHECKOV_NEW_TF_PARSER', 'True')):
            self.source_module_object: Optional[TFModule] = None
            self.for_each_index: Optional[Any] = None
            self.foreach_attrs: list[str] | None = None

    def add_module_connection(self, attribute_key: str, vertex_id: int) -> None:
        self.module_connections.setdefault(attribute_key, []).append(vertex_id)

    def extract_additional_changed_attributes(self, attribute_key: str) -> List[str]:
        # if the `attribute_key` starts with a `for_each.` we know the attribute can't be a dynamic attribute as it
        # represents the for_each of the block, so we don't need extract dynamic changed attributes
        # Fix: https://github.com/bridgecrewio/checkov/issues/4324
        if self.has_dynamic_block and not attribute_key.startswith('for_each'):
            return self._extract_dynamic_changed_attributes(attribute_key)
        return super().extract_additional_changed_attributes(attribute_key)

    def _extract_dynamic_changed_attributes(self, dynamic_attribute_key: str, nesting_prefix: str = '') -> List[str]:
        dynamic_changed_attributes: list[str] = []
        dynamic_attribute_key_parts = dynamic_attribute_key.split('.')
        try:
            remainder_key_parts = ['start_extract_dynamic_changed_attributes']  # For 1st iteration
            while remainder_key_parts:
                dynamic_for_each_index = dynamic_attribute_key_parts.index('for_each')
                dynamic_content_key_parts, remainder_key_parts = dynamic_attribute_key_parts[:dynamic_for_each_index],\
                    dynamic_attribute_key_parts[dynamic_for_each_index + 1:]
                dynamic_block_name = dynamic_content_key_parts[-1]
                dynamic_content_path = dynamic_content_key_parts + ['content']
                if dpath.search(self.attributes, dynamic_content_path):
                    dynamic_block_content = dpath.get(self.attributes, dynamic_content_path)
                    for key, value in dynamic_block_content.items():
                        key_path = ".".join(filter(None, [nesting_prefix, dynamic_block_name, key]))
                        self._collect_dynamic_dependent_keys(dynamic_block_name, value, key_path, dynamic_content_path, dynamic_changed_attributes)
                dynamic_attribute_key_parts = remainder_key_parts
            return dynamic_changed_attributes
        except ValueError:
            return dynamic_changed_attributes

    def _collect_dynamic_dependent_keys(self, dynamic_block_name: str, value: str | list[str] | dict[str, Any], key_path: str,
                                        dynamic_content_path: List[str], dynamic_changed_attributes: List[str]) -> None:
        if isinstance(value, str):
            dynamic_ref = f'{dynamic_block_name}.value'
            interpolation_matches = re.findall(INTERPOLATION_EXPR, value)
            for match in interpolation_matches:
                if dynamic_ref in match:
                    dynamic_changed_attributes.append(key_path)
        elif isinstance(value, list):
            for idx, sub_value in enumerate(value):
                self._collect_dynamic_dependent_keys(
                    dynamic_block_name, sub_value, f'{key_path}.{idx}', dynamic_content_path, dynamic_changed_attributes)
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict) and 'content' in sub_value.keys() and 'for_each' in sub_value.keys():
                    nested_dynamic_block_key_path = f'{".".join(dynamic_content_path)}.dynamic.{sub_key}.for_each'
                    dynamic_changed_attributes.extend(self._extract_dynamic_changed_attributes(nested_dynamic_block_key_path, nesting_prefix=dynamic_block_name))
                else:
                    self._collect_dynamic_dependent_keys(
                        dynamic_block_name, sub_value, f'{key_path}.{sub_key}', dynamic_content_path, dynamic_changed_attributes)

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

    def update_list_attribute(self, attribute_key: str, attribute_value: Any) -> None:
        """Updates list attributes with their index

        This needs to be overridden, because of our hcl parser adding a list around any value
        """

        if attribute_key not in self.attributes or isinstance(self.attributes[attribute_key][0], list):
            # sometimes the attribute_value is a list and replaces the whole value of the key, which makes it a normal value
            # ex. attribute_value = ["xyz"] and self.attributes[attribute_key][0] = "xyz"
            for idx, value in enumerate(attribute_value):
                self.attributes[f"{attribute_key}.{idx}"] = value

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

    def to_dict(self) -> dict[str, Any]:
        return {
            'attributes': self.attributes,
            'block_type': self.block_type,
            'breadcrumbs': self.breadcrumbs,
            'config': self.config,
            'id': self.id,
            'module_connections': self.module_connections,
            'module_dependency': self.module_dependency,
            'module_dependency_num': self.module_dependency_num,
            'name': self.name,
            'path': self.path,
            'source': self.source,
            'source_module': list(self.source_module)
        }
