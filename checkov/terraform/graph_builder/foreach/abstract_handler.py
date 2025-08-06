from __future__ import annotations

import abc
import json
import re
import typing
from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.env_vars_config import env_vars_config
from checkov.terraform.graph_builder.foreach.consts import COUNT_STRING, FOREACH_STRING, COUNT_KEY, EACH_VALUE, \
    EACH_KEY, REFERENCES_VALUES
from checkov.terraform.graph_builder.foreach.utils import append_virtual_resource
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import evaluate_terraform
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer

if typing.TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachAbstractHandler:
    def __init__(self, local_graph: TerraformLocalGraph) -> None:
        self.local_graph = local_graph

    @abc.abstractmethod
    def handle(self, resources_blocks: list[int]) -> None:
        pass

    @abc.abstractmethod
    def _create_new_foreach_resource(self, block_idx: int, foreach_idx: int, main_resource: TerraformBlock,
                                     new_key: int | str, new_value: int | str) -> str | None:
        pass

    @abc.abstractmethod
    def _create_new_resources_count(self, statement: int, block_idx: int) -> None:
        pass

    def _create_new_resources_foreach(self, statement: list[str] | dict[str, Any], block_idx: int) -> None:
        main_resource = self.local_graph.vertices[block_idx]
        virtual_resources_names: list[str] = []
        if isinstance(statement, list):
            for i, new_value in enumerate(statement):
                append_virtual_resource(
                    self._create_new_foreach_resource(block_idx, i, main_resource, new_key=new_value,
                                                      new_value=new_value), virtual_resources_names)
        if isinstance(statement, dict):
            for i, (new_key, new_value) in enumerate(statement.items()):
                append_virtual_resource(
                    self._create_new_foreach_resource(block_idx, i, main_resource, new_key, new_value),
                    virtual_resources_names)
        if env_vars_config.RAW_TF_IN_GRAPH_ENV:
            main_resource.config[CustomAttributes.VIRTUAL_RESOURCES] = virtual_resources_names
            self.local_graph.vertices.append(main_resource)

    @staticmethod
    def _render_sub_graph(sub_graph: TerraformLocalGraph, blocks_to_render: list[int]) -> None:
        renderer = TerraformVariableRenderer(sub_graph)
        renderer.vertices_index_to_render = blocks_to_render
        renderer.render_variables_from_local_graph()

    def _build_sub_graph(self, blocks_to_render: list[int]) -> TerraformLocalGraph:
        from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

        sub_graph = TerraformLocalGraph(self.local_graph.module)
        sub_graph.vertices = [{}] * len(self.local_graph.vertices)  # type:ignore[list-item]  # are correctly set in the next lines
        for i, block in enumerate(self.local_graph.vertices):
            if not (block.block_type == BlockType.RESOURCE and i not in blocks_to_render):
                sub_graph.vertices[i] = pickle_deepcopy(block)
        sub_graph.edges = [
            edge for edge in self.local_graph.edges if
            (sub_graph.vertices[edge.dest] and sub_graph.vertices[edge.origin])
        ]
        sub_graph.in_edges = self.local_graph.in_edges
        sub_graph.out_edges = self.local_graph.out_edges
        return sub_graph

    @staticmethod
    def _pop_foreach_attrs(attrs: dict[str, Any]) -> None:
        attrs.pop(COUNT_STRING, None)
        attrs.pop(FOREACH_STRING, None)

    @staticmethod
    def __update_str_attrs(attrs: dict[str, Any], key_to_change: str, val_to_change: str | dict[str, Any],
                           k: str) -> bool:
        if key_to_change not in attrs[k]:
            return False
        if attrs[k] == "${" + key_to_change + "}":
            attrs[k] = val_to_change
            return True
        elif f"{key_to_change}." in attrs[k] and isinstance(val_to_change, dict):
            key = attrs[k].replace("}", "").split('.')[-1]
            attrs[k] = val_to_change.get(key)
            return True
        else:
            attrs[k] = attrs[k].replace("${" + key_to_change + "}", str(val_to_change))
            attrs[k] = attrs[k].replace(key_to_change, str(val_to_change))
            return True

    @staticmethod
    def _build_key_to_val_changes(main_resource: TerraformBlock, new_val: str | int, new_key: str | int | None) \
            -> dict[str, str | int | None]:
        if main_resource.attributes.get(COUNT_STRING):
            return {COUNT_KEY: new_val}

        return {
            EACH_VALUE: new_val,
            EACH_KEY: new_key
        }

    def _update_foreach_attrs(self, config_attrs: dict[str, Any], key_to_val_changes: dict[str, Any],
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
                elif isinstance(v, dict):
                    nested_attrs = self._update_attributes(v, {key_to_change: val_to_change})
                    foreach_attributes.extend([k + '.' + na for na in nested_attrs])
                elif isinstance(v, list) and len(v) == 1 and isinstance(v[0], dict):
                    nested_attrs = self._update_attributes(v[0], {key_to_change: val_to_change})
                    foreach_attributes.extend([k + '.' + na for na in nested_attrs])
                elif isinstance(v, list) and len(v) == 1 and isinstance(v[0], str) and key_to_change in v[0]:
                    if attrs[k][0] == "${" + key_to_change + "}":
                        attrs[k][0] = val_to_change
                        v_changed = True
                    elif f"{key_to_change}." in attrs[k][0] and isinstance(val_to_change, dict):
                        for inner_key, inner_value in val_to_change.items():
                            str_to_replace = f"{key_to_change}.{inner_key}"
                            if str_to_replace in attrs[k][0]:
                                dollar_wrapped_str_to_replace = "${" + str_to_replace + "}"
                                if attrs[k][0] == dollar_wrapped_str_to_replace:
                                    attrs[k][0] = inner_value
                                    v_changed = True
                                    # Since we assigned a value to attrs[k][0] we don't need to check the value again for
                                    # interpolations to replace, we can break out of the loop
                                    break
                                elif dollar_wrapped_str_to_replace in attrs[k][0]:
                                    str_to_replace = dollar_wrapped_str_to_replace
                                attrs[k][0] = attrs[k][0].replace(str_to_replace, str(inner_value))
                                v_changed = True
                    else:
                        attrs[k][0] = attrs[k][0].replace("${" + key_to_change + "}", str(val_to_change))
                        if self.need_to_add_quotes(attrs[k][0], key_to_change):
                            attrs[k][0] = attrs[k][0].replace(key_to_change, f'"{str(val_to_change)}"')
                        else:
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

    def _handle_static_statement(self, block_index: int, sub_graph: TerraformLocalGraph | None = None) -> \
            list[str] | dict[str, Any] | int | None:
        attrs = self.local_graph.vertices[block_index].attributes if not sub_graph \
            else sub_graph.vertices[block_index].attributes
        foreach_statement = attrs.get(FOREACH_STRING)
        count_statement = attrs.get(COUNT_STRING)
        if foreach_statement:
            return self._handle_static_foreach_statement(foreach_statement)
        if count_statement:
            return self._handle_static_count_statement(count_statement)
        return None

    def _handle_static_foreach_statement(self, statement: list[str] | dict[str, Any]) \
            -> list[str] | dict[str, Any] | None:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        evaluated_statement = evaluate_terraform(statement)
        if isinstance(evaluated_statement, str):
            try:
                evaluated_statement = json.loads(evaluated_statement)
            except ValueError:
                pass
        if isinstance(evaluated_statement, set):
            evaluated_statement = list(evaluated_statement)
        if isinstance(evaluated_statement, (dict, list)) and all(isinstance(val, str) for val in evaluated_statement):
            return evaluated_statement
        return None

    def _handle_static_count_statement(self, statement: list[str] | int) -> int | None:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        evaluated_statement = evaluate_terraform(statement)
        if isinstance(evaluated_statement, int):
            return evaluated_statement
        return None

    def _is_static_foreach_statement(self, statement: str | list[str] | dict[str, Any]) -> bool:
        if isinstance(statement, list):
            if len(statement) == 1 and not statement[0]:
                return True
            statement = self.extract_from_list(statement)
        if isinstance(statement, str) and re.search(REFERENCES_VALUES, statement):
            return False
        if isinstance(statement, (list, dict)):
            result = True
            for s in statement:
                result &= self._is_static_foreach_statement(s)
            return result
        return True

    def _is_static_count_statement(self, statement: list[str] | int) -> bool:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        if isinstance(statement, int):
            return True
        if isinstance(statement, str) and not re.search(REFERENCES_VALUES, statement):
            return True
        return False

    def _is_static_statement(self, block_index: int, sub_graph: TerraformLocalGraph | None = None) -> bool:
        """
        foreach statement can be list/map of strings or map, if its string we need to render it for sure.
        """
        block = self.local_graph.vertices[block_index] if not sub_graph else sub_graph.vertices[block_index]
        foreach_statement = evaluate_terraform(block.attributes.get(FOREACH_STRING))
        count_statement = evaluate_terraform(block.attributes.get(COUNT_STRING))
        if foreach_statement:
            return self._is_static_foreach_statement(foreach_statement)
        if count_statement:
            return self._is_static_count_statement(count_statement)
        return False

    @staticmethod
    def extract_from_list(val: Any) -> Any:
        return val[0] if len(val) == 1 and isinstance(val[0], (str, int, list)) else val

    @staticmethod
    def need_to_add_quotes(code: str, key: str) -> bool:
        if "lower" in code or "upper" in code:
            patterns = (r'lower\(' + key + r'\)', r'upper\(' + key + r'\)')
            for pattern in patterns:
                if re.search(pattern, code):
                    return True

        if f'[{key}]' in code:
            return True

        return False
