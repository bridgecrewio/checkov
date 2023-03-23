from __future__ import annotations

import abc
import typing
from copy import deepcopy
from typing import Any

from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.terraform import TFModule
from checkov.terraform.graph_builder.foreach.consts import COUNT_STRING, FOREACH_STRING, COUNT_KEY, EACH_VALUE, EACH_KEY
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer

if typing.TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachAbstractHandler:
    def __init__(self, local_graph: TerraformLocalGraph) -> None:
        self.local_graph = local_graph

    @abc.abstractmethod
    def handle(self, resources_blocks: list[int]) -> None:
        pass

    def _create_new_resources_foreach(self, statement: list[str] | dict[str, Any], block_idx: int) -> None:
        main_resource = self.local_graph.vertices[block_idx]
        if isinstance(statement, list):
            for i, new_value in enumerate(statement):
                self._create_new_foreach_resource(block_idx, i, main_resource, new_key=new_value, new_value=new_value)
        if isinstance(statement, dict):
            for i, (new_key, new_value) in enumerate(statement.items()):
                self._create_new_foreach_resource(block_idx, i, main_resource, new_key, new_value)

    @abc.abstractmethod
    def _create_new_foreach_resource(self, block_idx: int, foreach_idx: int, main_resource: TerraformBlock,
                                     new_key: int | str, new_value: int | str) -> None:
        pass

    @abc.abstractmethod
    def _create_new_resources_count(self, statement: int, block_idx: int) -> None:
        pass

    @staticmethod
    def _render_sub_graph(sub_graph: TerraformLocalGraph, blocks_to_render: list[int]) -> None:
        renderer = TerraformVariableRenderer(sub_graph)
        renderer.vertices_index_to_render = blocks_to_render
        renderer.render_variables_from_local_graph()

    def _build_sub_graph(self, blocks_to_render: list[int]) -> TerraformLocalGraph:
        from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

        module = deepcopy(self.local_graph.module)
        sub_graph = TerraformLocalGraph(module)
        sub_graph.vertices = [{}] * len(self.local_graph.vertices)
        for i, block in enumerate(self.local_graph.vertices):
            if not (block.block_type == BlockType.RESOURCE and i not in blocks_to_render):
                sub_graph.vertices[i] = deepcopy(block)
        sub_graph.edges = [
            deepcopy(edge) for edge in self.local_graph.edges if (sub_graph.vertices[edge.dest] and sub_graph.vertices[edge.origin])
        ]
        sub_graph.in_edges = deepcopy(self.local_graph.in_edges)
        sub_graph.out_edges = deepcopy(self.local_graph.out_edges)
        return sub_graph

    @staticmethod
    def _update_nested_tf_module_foreach_idx(original_foreach_or_count_key: int | str, original_module_key: TFModule,
                                             tf_moudle: TFModule) -> None:
        original_module_key.foreach_idx = None  # Make sure it is always None even if we didn't override it previously
        while tf_moudle is not None:
            if tf_moudle == original_module_key:
                tf_moudle.foreach_idx = original_foreach_or_count_key
                break
            tf_moudle = tf_moudle.nested_tf_module

    @staticmethod
    def _pop_foreach_attrs(attrs: dict[str, Any]) -> None:
        attrs.pop(COUNT_STRING, None)
        attrs.pop(FOREACH_STRING, None)

    @staticmethod
    def __update_str_attrs(attrs: dict[str | int, Any], key_to_change: str, val_to_change: str, k: str | int) -> bool:
        if attrs[k] == "${" + key_to_change + "}":
            attrs[k] = val_to_change
            return True
        else:
            attrs[k] = attrs[k].replace("${" + key_to_change + "}", str(val_to_change))
            attrs[k] = attrs[k].replace(key_to_change, str(val_to_change))
            return True

    @staticmethod
    def _build_key_to_val_changes(main_resource: TerraformBlock, new_val: str, new_key: str) -> dict[str, str | int]:
        if main_resource.attributes.get(COUNT_STRING):
            return {COUNT_KEY: new_val}

        return {
            EACH_VALUE: new_val,
            EACH_KEY: new_key
        }

    def _update_foreach_attrs(self, config_attrs: dict[str | int, Any], key_to_val_changes: dict[str, Any],
                              new_resource: TerraformBlock) -> None:
        self._pop_foreach_attrs(new_resource.attributes)
        self._pop_foreach_attrs(config_attrs)
        self._update_attributes(new_resource.attributes, key_to_val_changes)
        foreach_attrs = self._update_attributes(config_attrs, key_to_val_changes)
        new_resource.foreach_attrs = foreach_attrs

    def _update_attributes(self, attrs: dict[str, Any], key_to_val_changes: dict[str, Any]) -> list[str]:
        foreach_attributes: list[str] = []
        for key_to_change, val_to_change in key_to_val_changes.items():
            for k, v in attrs.items():
                v_changed = False
                if isinstance(v, str):
                    v_changed = self.__update_str_attrs(attrs, key_to_change, val_to_change, k)
                if isinstance(v, dict):
                    nested_attrs = self._update_attributes(v, {key_to_change: val_to_change})
                    foreach_attributes.extend([k + '.' + na for na in nested_attrs])
                if isinstance(v, list) and len(v) == 1 and isinstance(v[0], dict):
                    nested_attrs = self._update_attributes(v[0], {key_to_change: val_to_change})
                    foreach_attributes.extend([k + '.' + na for na in nested_attrs])
                elif isinstance(v, list) and len(v) == 1 and isinstance(v[0], str) and key_to_change in v[0]:
                    if attrs[k][0] == "${" + key_to_change + "}":
                        attrs[k][0] = val_to_change
                        v_changed = True
                    else:
                        attrs[k][0] = attrs[k][0].replace("${" + key_to_change + "}", str(val_to_change))
                        attrs[k][0] = attrs[k][0].replace(key_to_change, str(val_to_change))
                        v_changed = True
                elif isinstance(v, list) and len(v) == 1 and isinstance(v[0], list):
                    for i, item in enumerate(v):
                        if isinstance(item, str) and (key_to_change in item or "${" + key_to_change + "}" in item):
                            if v[i] == "${" + key_to_change + "}":
                                v[i] = val_to_change
                                v_changed = True
                            else:
                                v[i] = item.replace("${" + key_to_change + "}", str(val_to_change))
                                v[i] = v[i].replace(key_to_change, str(val_to_change))
                                v_changed = True
                if v_changed:
                    foreach_attributes.append(k)
        return foreach_attributes

    @staticmethod
    def _update_block_name_and_id(block: TerraformBlock, idx: int | str) -> str:
        # Note it is important to use `\"` inside the string,
        # as the string `["` is the separator for `foreach` in terraform.
        # In `count` it is just `[`
        idx_with_separator = f'\"{idx}\"' if isinstance(idx, str) else f'{idx}'
        new_block_id = f"{block.id}[{idx_with_separator}]"
        new_block_name = f"{block.name}[{idx_with_separator}]"

        if block.block_type == BlockType.MODULE:
            block.config[new_block_name] = block.config.pop(block.name)
        block.id = new_block_id
        block.name = new_block_name
        return idx_with_separator

    @staticmethod
    def _update_resolved_entry_for_tf_definition(child: TerraformBlock, original_foreach_or_count_key: int | str,
                                                 original_module_key: TFModule) -> None:
        if child.block_type == BlockType.RESOURCE:
            child_name, child_type = child.name.split('.')
            config = child.config[child_name][child_type]
        else:
            config = child.config.get(child.name)
        if isinstance(config, dict) and config.get(RESOLVED_MODULE_ENTRY_NAME) is not None:
            tf_moudle: TFModule = config[RESOLVED_MODULE_ENTRY_NAME][0].tf_source_modules
            ForeachAbstractHandler._update_nested_tf_module_foreach_idx(original_foreach_or_count_key, original_module_key,
                                                                        tf_moudle)
