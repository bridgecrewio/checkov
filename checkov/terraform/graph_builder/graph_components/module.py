from __future__ import annotations

import json
import os
from typing import List, Dict, Any, Set, Callable, Tuple, TYPE_CHECKING, cast
from ast import literal_eval

from checkov.common.typing import TFDefinitionKeyType
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform import TFDefinitionKey
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.common.graph.graph_builder import CustomAttributes, wrap_reserved_attributes, reserved_attributes_to_scan
from checkov.terraform.parser_functions import handle_dynamic_values
from hcl2 import START_LINE, END_LINE

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

_AddBlockTypeCallable: TypeAlias = "Callable[[Module, list[dict[str, dict[str, Any]]], TFDefinitionKeyType], None]"


class Module:
    def __init__(
            self,
            source_dir: str,
            external_modules_source_map: Dict[Tuple[str, str], str],
    ) -> None:
        # when adding a new field be sure to add it to the equality function below
        self.external_modules_source_map = external_modules_source_map
        self.path = ""
        self.blocks: List[TerraformBlock] = []
        self.customer_name = ""
        self.account_id = ""
        self.source = ""
        self.resources_types: Set[str] = set()
        self.source_dir = source_dir
        self.render_dynamic_blocks_env_var = os.getenv('CHECKOV_RENDER_DYNAMIC_MODULES', 'True')
        self.temp_tf_definition: dict[TFDefinitionKey, dict[str, Any]] = {}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Module):
            return False

        return self.external_modules_source_map == other.external_modules_source_map and \
            self.path == other.path and \
            self.customer_name == other.customer_name and \
            self.account_id == other.account_id and \
            self.source == other.source and \
            self.resources_types == other.resources_types and \
            self.source_dir == other.source_dir and \
            self.blocks == other.blocks

    def to_dict(self) -> dict[str, Any]:
        return {
            'external_modules_source_map': self._to_dict_external_modules_source_map(),
            'path': self.path,
            'customer_name': self.customer_name,
            'account_id': self.account_id,
            'source': self.source,
            'resources_types': self.resources_types,
            'source_dir': self.source_dir,
            'render_dynamic_blocks_env_var': self.render_dynamic_blocks_env_var,
            'blocks': [block.to_dict() for block in self.blocks]
        }

    @staticmethod
    def from_dict(module_dict: dict[str, Any]) -> Module:
        module = Module(source_dir=module_dict.get('source_dir', ''),
                        external_modules_source_map=Module._from_dict_external_modules_source_map(module_dict)
                        )
        module.blocks = [TerraformBlock.from_dict(block) for block in module_dict.get('blocks', [])]
        module.path = module_dict.get('path', '')
        module.customer_name = module_dict.get('customer_name', '')
        module.account_id = module_dict.get('account_id', '')
        module.source = module_dict.get('source', '')
        module.resources_types = module_dict.get('resources_types', set())
        module.source_dir = module_dict.get('source_dir', '')
        module.render_dynamic_blocks_env_var = module_dict.get('render_dynamic_blocks_env_var', '')
        return module

    def _to_dict_external_modules_source_map(self) -> dict[str, str]:
        return {str(k_tuple): v for k_tuple, v in self.external_modules_source_map.items()}

    @staticmethod
    def _from_dict_external_modules_source_map(module_dict: dict[str, Any]) -> dict[tuple[str, str], Any]:
        return {literal_eval(k_tuple): v for k_tuple, v in module_dict.get('external_modules_source_map', {}).items()}

    def add_blocks(
            self, block_type: str, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType, source: str
    ) -> None:
        self.source = source
        if block_type in self._block_type_to_func:
            self._block_type_to_func[block_type](self, blocks, path)

    def _add_to_blocks(self, block: TerraformBlock) -> None:
        if isinstance(block.path, str):
            block.source_module_object = None
            block.path = block.path
        else:
            block.source_module_object = block.path.tf_source_modules
            block.path = block.path.file_path
        self.blocks.append(block)
        return

    def _add_provider(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for provider_dict in blocks:
            for name in provider_dict:
                attributes = provider_dict[name]
                if START_LINE not in attributes or END_LINE not in attributes:
                    return
                provider_name = name
                if isinstance(attributes, dict):
                    alias = attributes.get("alias")
                    if alias:
                        provider_name = f"{provider_name}.{alias[0]}"
                provider_block = TerraformBlock(
                    block_type=BlockType.PROVIDER,
                    name=provider_name,
                    config=provider_dict,
                    path=path,
                    attributes=attributes,
                    source=self.source,
                )
                self._add_to_blocks(provider_block)

    def _add_variable(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for variable_dict in blocks:
            for name in variable_dict:
                attributes = variable_dict[name]
                variable_block = TerraformBlock(
                    block_type=BlockType.VARIABLE,
                    name=name,
                    config=variable_dict,
                    path=path,
                    attributes=attributes,
                    source=self.source,
                )
                self._add_to_blocks(variable_block)

    def _add_locals(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for blocks_section in blocks:
            for name in blocks_section:
                if name in (START_LINE, END_LINE):
                    # locals block generates single block sections for the start/end lines
                    continue

                local_block = TerraformBlock(
                    block_type=BlockType.LOCALS,
                    name=name,
                    config={name: blocks_section[name]},
                    path=path,
                    attributes={name: blocks_section[name]},
                    source=self.source,
                )
                self._add_to_blocks(local_block)

    def _add_output(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for output_dict in blocks:
            for name, attributes in output_dict.items():
                if isinstance(attributes, dict):
                    output_block = TerraformBlock(
                        block_type=BlockType.OUTPUT,
                        name=name,
                        config=output_dict,
                        path=path,
                        attributes={"value": attributes.get("value")},
                        source=self.source,
                    )
                    self._add_to_blocks(output_block)

    def _add_module(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for module_dict in blocks:
            for name, attributes in module_dict.items():
                if isinstance(attributes, dict):
                    module_block = TerraformBlock(
                        block_type=BlockType.MODULE,
                        name=name,
                        config=module_dict,
                        path=path,
                        attributes=attributes,
                        source=self.source,
                    )
                    self._add_to_blocks(module_block)

    def _alter_reserved_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reserved attributes (like `resource_type`) needs to be altered in order to be considered in scanning
        """
        updated_attributes = pickle_deepcopy(attributes)
        for reserved_attribute in reserved_attributes_to_scan:
            if reserved_attribute in updated_attributes:
                updated_attributes[wrap_reserved_attributes(reserved_attribute)] = updated_attributes[reserved_attribute]
        return updated_attributes

    def _add_resource(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for resource_dict in blocks:
            for resource_type, resources in resource_dict.items():
                self.resources_types.add(resource_type)
                for name, resource_conf in resources.items():
                    attributes = self.clean_bad_characters(resource_conf)
                    dynamic_attributes = None
                    if not isinstance(attributes, dict):
                        continue
                    if self.render_dynamic_blocks_env_var.lower() == 'false':
                        has_dynamic_block = False
                    else:
                        old_attributes = pickle_deepcopy(attributes)
                        has_dynamic_block = handle_dynamic_values(attributes)
                        dynamic_attributes = {k: attributes[k] for k in set(attributes) - set(old_attributes)}
                    provisioner = attributes.get("provisioner")
                    if provisioner:
                        self._handle_provisioner(provisioner, attributes)
                    attributes = self._alter_reserved_attributes(attributes)
                    attributes[CustomAttributes.RESOURCE_TYPE] = [resource_type]
                    block_name = f"{resource_type}.{name}"
                    resource_block = TerraformBlock(
                        block_type=BlockType.RESOURCE,
                        name=block_name,
                        config=self.clean_bad_characters(resource_dict),
                        path=path,
                        attributes=attributes,
                        id=block_name,
                        source=self.source,
                        has_dynamic_block=has_dynamic_block,
                        dynamic_attributes=dynamic_attributes
                    )
                    self._add_to_blocks(resource_block)

    @staticmethod
    def clean_bad_characters(resource_conf: dict[str, Any]) -> dict[str, Any]:
        try:
            return cast("dict[str, Any]", json.loads(json.dumps(resource_conf).replace("\\\\", "\\")))
        except json.JSONDecodeError:
            return resource_conf

    def _add_data(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for data_dict in blocks:
            for data_type in data_dict:
                for name in data_dict[data_type]:
                    block_name = f"{data_type}.{name}"
                    data_block = TerraformBlock(
                        block_type=BlockType.DATA,
                        name=block_name,
                        config=data_dict,
                        path=path,
                        attributes=data_dict.get(data_type, {}).get(name, {}),
                        id=block_name,
                        source=self.source,
                    )
                    self._add_to_blocks(data_block)

    def _add_terraform_block(self, blocks: List[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for terraform_dict in blocks:
            terraform_block = TerraformBlock(
                block_type=BlockType.TERRAFORM,
                name="",
                config=terraform_dict,
                path=path,
                attributes=terraform_dict,
                source=self.source,
            )
            self._add_to_blocks(terraform_block)

    def _add_tf_var(self, blocks: list[Dict[str, Dict[str, Any]]], path: TFDefinitionKeyType) -> None:
        for block in blocks:
            for tf_var_name, attributes in block.items():
                tfvar_block = TerraformBlock(
                    block_type=BlockType.TF_VARIABLE,
                    name=tf_var_name,
                    config={tf_var_name: attributes},
                    path=path,
                    attributes=attributes,
                    source=self.source,
                )
                self._add_to_blocks(tfvar_block)

    @staticmethod
    def _handle_provisioner(provisioner: List[Dict[str, Any]], attributes: Dict[str, Any]) -> None:
        for pro in provisioner:
            if pro.get("local-exec"):
                inner_attributes = TerraformBlock.get_inner_attributes("provisioner/local-exec", pro["local-exec"])
                attributes.update(inner_attributes)
            elif pro.get("remote-exec"):
                inner_attributes = TerraformBlock.get_inner_attributes("provisioner/remote-exec", pro["remote-exec"])
                attributes.update(inner_attributes)
        del attributes["provisioner"]

    def get_resources_types(self) -> List[str]:
        return list(self.resources_types)

    _block_type_to_func: Dict[str, _AddBlockTypeCallable] = {  # noqa: CCE003  # a static attribute
        BlockType.DATA: _add_data,
        BlockType.LOCALS: _add_locals,
        BlockType.MODULE: _add_module,
        BlockType.OUTPUT: _add_output,
        BlockType.PROVIDER: _add_provider,
        BlockType.RESOURCE: _add_resource,
        BlockType.TERRAFORM: _add_terraform_block,
        BlockType.TF_VARIABLE: _add_tf_var,
        BlockType.VARIABLE: _add_variable,
    }
