from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import List, Dict, Any, Set, Callable, Tuple, TYPE_CHECKING

from checkov.common.runners.base_runner import strtobool
from checkov.common.util.parser_utils import get_abs_path, get_module_from_full_path
from checkov.terraform.checks.utils.dependency_path_handler import unify_dependency_path
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.parser_functions import handle_dynamic_values
from hcl2 import START_LINE, END_LINE

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

_AddBlockTypeCallable: TypeAlias = "Callable[[Module, list[dict[str, dict[str, Any]]], str], None]"


class Module:
    def __init__(
        self,
        source_dir: str,
        module_dependency_map: Dict[str, List[List[str]]],
        module_address_map: Dict[Tuple[str, str], str],
        external_modules_source_map: Dict[Tuple[str, str], str],
        dep_index_mapping: Dict[Tuple[str, str], List[str]],
    ) -> None:
        self.dep_index_mapping = dep_index_mapping
        self.module_dependency_map = module_dependency_map
        self.module_address_map = module_address_map
        self.external_modules_source_map = external_modules_source_map
        self.path = ""
        self.blocks: List[TerraformBlock] = []
        self.customer_name = ""
        self.account_id = ""
        self.source = ""
        self.resources_types: Set[str] = set()
        self.source_dir = source_dir
        self.render_dynamic_blocks_env_var = os.getenv('CHECKOV_RENDER_DYNAMIC_MODULES', 'True')
        self.enable_nested_modules = strtobool(os.getenv('CHECKOV_ENABLE_NESTED_MODULES', 'True'))

    def add_blocks(
        self, block_type: BlockType, blocks: List[Dict[str, Dict[str, Any]]], path: str, source: str
    ) -> None:
        self.source = source
        if block_type in self._block_type_to_func:
            self._block_type_to_func[block_type](self, blocks, path)

    def _add_to_blocks(self, block: TerraformBlock) -> None:
        if self.enable_nested_modules:
            block.module_dependency, block.module_dependency_num = get_module_from_full_path(block.path)
            block.path = get_abs_path(block.path)
            self.blocks.append(block)
            return

        dependencies = self.module_dependency_map.get(os.path.dirname(block.path), [])
        module_dependency_num = ""
        if not dependencies:
            dependencies = [[]]
        for dep_idx, dep_trail in enumerate(dependencies):
            if dep_idx > 0:
                block = deepcopy(block)
            block.module_dependency = unify_dependency_path(dep_trail)

            if block.module_dependency:
                module_dependency_numbers = self.dep_index_mapping.get((block.path, dep_trail[-1]), [])
                for mod_idx, module_dep_num in enumerate(module_dependency_numbers):
                    if mod_idx > 0:
                        block = deepcopy(block)
                    block.module_dependency_num = module_dep_num
                    self.blocks.append(block)
            else:
                block.module_dependency_num = module_dependency_num
                self.blocks.append(block)

    def _add_provider(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
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

    def _add_variable(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
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

    def _add_locals(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
        for blocks_section in blocks:
            for name in blocks_section:
                local_block = TerraformBlock(
                    block_type=BlockType.LOCALS,
                    name=name,
                    config={name: blocks_section[name]},
                    path=path,
                    attributes={name: blocks_section[name]},
                    source=self.source,
                )
                self._add_to_blocks(local_block)

    def _add_output(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
        for output_dict in blocks:
            for name in output_dict:
                if type(output_dict[name]) is not dict:
                    continue
                output_block = TerraformBlock(
                    block_type=BlockType.OUTPUT,
                    name=name,
                    config=output_dict,
                    path=path,
                    attributes={"value": output_dict[name].get("value")},
                    source=self.source,
                )
                self._add_to_blocks(output_block)

    def _add_module(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
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

    def _add_resource(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
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
                        old_attributes = deepcopy(attributes)
                        has_dynamic_block = handle_dynamic_values(attributes)
                        dynamic_attributes = {k: attributes[k] for k in set(attributes) - set(old_attributes)}
                    provisioner = attributes.get("provisioner")
                    if provisioner:
                        self._handle_provisioner(provisioner, attributes)
                    attributes["resource_type"] = [resource_type]
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
    def clean_bad_characters(resource_conf):
        try:
            return json.loads(json.dumps(resource_conf).replace("\\\\", "\\"))
        except json.JSONDecodeError:
            return resource_conf

    def _add_data(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
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

    def _add_terraform_block(self, blocks: List[Dict[str, Dict[str, Any]]], path: str) -> None:
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

    def _add_tf_var(self, blocks: Dict[str, Dict[str, Any]], path: str) -> None:
        for tf_var_name, attributes in blocks.items():
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

    _block_type_to_func: Dict[BlockType, _AddBlockTypeCallable] = {  # noqa: CCE003  # a static attribute
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
