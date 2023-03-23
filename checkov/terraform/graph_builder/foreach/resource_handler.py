from __future__ import annotations

import logging
import json
import re
from collections import defaultdict
from copy import deepcopy
from typing import Any, Optional

from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.terraform.graph_builder.foreach.consts import FOREACH_STRING, COUNT_STRING, REFERENCES_VALUES, \
    FOR_EACH_BLOCK_TYPE, COUNT_KEY, EACH_KEY, EACH_VALUE
from checkov.terraform.modules.module_objects import TFModule
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.variable_rendering.renderer import TerraformVariableRenderer
from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import evaluate_terraform
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph

class ForeachResourceHandler(object):
    def __init__(self, local_graph: TerraformLocalGraph) -> None:
        self.local_graph = local_graph

    def handle(self, resources_blocks: list[int]) -> None:
        block_index_to_statement = self._get_statements(resources_blocks)
        self._create_new_resources(block_index_to_statement)

    def _get_statements(self, resources_blocks: list[int]) -> FOR_EACH_BLOCK_TYPE:
        if not resources_blocks:
            return {}
        block_index_to_statement: FOR_EACH_BLOCK_TYPE = {}
        for block_index, block in enumerate(self.local_graph.vertices):
            if not (FOREACH_STRING in block.attributes or COUNT_STRING in block.attributes):
                continue
            foreach_statement = self._get_static_foreach_statement(block_index)
            block_index_to_statement[block_index] = foreach_statement
        blocks_to_render = [block_idx for block_idx, statement in block_index_to_statement.items() if statement is None]
        if blocks_to_render:
            rendered_statements = self._handle_dynamic_statement(blocks_to_render)
            block_index_to_statement.update(rendered_statements)
        return block_index_to_statement

    def _get_static_foreach_statement(self, block_index: int) -> Optional[list[str] | dict[str, Any]]:
        attributes = self.local_graph.vertices[block_index].attributes
        if not attributes.get(FOREACH_STRING) and not attributes.get(COUNT_STRING):
            return
        try:
            if self._is_static_statement(block_index):
                return self._handle_static_statement(block_index)
            else:
                return None
        except Exception as e:
            logging.info(f"Cant get foreach statement for block: {self.local_graph.vertices[block_index]}, error: {str(e)}")
            return None

    def _is_static_foreach_statement(self, statement: list[str] | dict[str, Any]) -> bool:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        if isinstance(statement, str) and re.search(REFERENCES_VALUES, statement):
            return False
        if isinstance(statement, (list, dict)) and any([re.search(REFERENCES_VALUES, s) for s in statement]):
            return False
        return True

    def _is_static_count_statement(self, statement: list[str] | int) -> bool:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        if isinstance(statement, int):
            return True
        if isinstance(statement, str) and not re.search(REFERENCES_VALUES, statement):
            return True
        return False

    def _is_static_statement(self, block_index: int, sub_graph: Optional[l_graph.TerraformLocalGraph] = None) -> bool:
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
    def extract_from_list(val: list[str] | list[int] | list[list[str]]) -> list[str] | list[int] | int | str:
        return val[0] if len(val) == 1 and isinstance(val[0], (str, int, list)) else val

    def _handle_static_foreach_statement(self, statement: list[str] | dict[str, Any]) -> Optional[list[str] | dict[str, Any]]:
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
        return

    def _handle_static_count_statement(self, statement: list[str] | int) -> Optional[int]:
        if isinstance(statement, list):
            statement = self.extract_from_list(statement)
        evaluated_statement = evaluate_terraform(statement)
        if isinstance(evaluated_statement, int):
            return evaluated_statement
        return

    def _handle_static_statement(self, block_index: int, sub_graph: Optional[l_graph.TerraformLocalGraph] = None) -> Optional[list[str] | dict[str, Any] | int]:
        attrs = self.local_graph.vertices[block_index].attributes if not sub_graph else sub_graph.vertices[block_index].attributes
        foreach_statement = attrs.get(FOREACH_STRING)
        count_statement = attrs.get(COUNT_STRING)
        if foreach_statement:
            return self._handle_static_foreach_statement(foreach_statement)
        if count_statement:
            return self._handle_static_count_statement(count_statement)
        return

    def _handle_dynamic_statement(self, blocks_to_render: list[int]) -> FOR_EACH_BLOCK_TYPE:
        rendered_statements_by_idx: FOR_EACH_BLOCK_TYPE = {}
        sub_graph = self._build_sub_graph(blocks_to_render)
        self._render_sub_graph(sub_graph, blocks_to_render)
        for block_idx in blocks_to_render:
            if not self._is_static_statement(block_idx, sub_graph):
                rendered_statements_by_idx[block_idx] = None
            else:
                rendered_statements_by_idx[block_idx] = self._handle_static_statement(block_idx, sub_graph)
        return rendered_statements_by_idx

    @staticmethod
    def _render_sub_graph(sub_graph: l_graph.TerraformLocalGraph, blocks_to_render: list[int]) -> None:
        renderer = TerraformVariableRenderer(sub_graph)
        renderer.vertices_index_to_render = blocks_to_render
        renderer.render_variables_from_local_graph()

    def _build_sub_graph(self, blocks_to_render: list[int]) -> l_graph.TerraformLocalGraph:
        module = deepcopy(self.local_graph.module)
        sub_graph = l_graph.TerraformLocalGraph(module)
        sub_graph.vertices = [{}] * len(self.local_graph.vertices)
        for i, block in enumerate(self.local_graph.vertices):
            if not (block.block_type == BlockType.RESOURCE and i not in blocks_to_render):
                sub_graph.vertices[i] = deepcopy(block)  # type: ignore
        sub_graph.edges = [
            deepcopy(edge) for edge in self.local_graph.edges if (sub_graph.vertices[edge.dest] and sub_graph.vertices[edge.origin])
        ]
        sub_graph.in_edges = deepcopy(self.local_graph.in_edges)
        sub_graph.out_edges = deepcopy(self.local_graph.out_edges)
        return sub_graph

    def _create_new_resources_count(self, statement: int, block_idx: int) -> None:
        main_resource = self.local_graph.vertices[block_idx]
        for i in range(statement):
            if main_resource.block_type == BlockType.MODULE:
                self._create_new_module(main_resource, i, resource_idx=block_idx, foreach_idx=i)
            elif main_resource.block_type == BlockType.RESOURCE:
                self._create_new_resource(main_resource, i, resource_idx=block_idx, foreach_idx=i)
        if main_resource.block_type == BlockType.MODULE:
            for i in range(statement):
                should_override = True if i == 0 else False
                self._update_module_children(main_resource, i, should_override_foreach_key=should_override)

    def _update_module_children(self, main_resource: TerraformBlock,
                                original_foreach_or_count_key: int | str,
                                should_override_foreach_key: bool = True) -> None:
        original_module_key = TFModule(path=main_resource.path, name=main_resource.name,
                                       nested_tf_module=main_resource.source_module_object)

        if not should_override_foreach_key:
            original_module_key.foreach_idx = original_foreach_or_count_key

        self._update_children_foreach_index(original_foreach_or_count_key, original_module_key,
                                            should_override_foreach_key=should_override_foreach_key)

    def _update_children_foreach_index(self, original_foreach_or_count_key: int | str, original_module_key: TFModule,
                                       current_module_key: TFModule | None = None, should_override_foreach_key: bool = True) -> None:
        """
        Go through all child vertices and update source_module_object with foreach_idx
        """
        if current_module_key is None:
            current_module_key = deepcopy(original_module_key)
        if current_module_key not in self.local_graph.vertices_by_module_dependency:
            return
        values = self.local_graph.vertices_by_module_dependency[current_module_key].values()
        for child_indexes in values:
            for child_index in child_indexes:
                child = self.local_graph.vertices[child_index]

                ForeachResourceHandler._update_nested_tf_module_foreach_idx(original_foreach_or_count_key, original_module_key,
                                                                            child.source_module_object)
                self._update_resolved_entry_for_tf_definition(child, original_foreach_or_count_key, original_module_key)

                # Important to copy to avoid changing the object by reference
                child_source_module_object_copy = deepcopy(child.source_module_object)
                if should_override_foreach_key:
                    child_source_module_object_copy.foreach_idx = None

                child_module_key = TFModule(path=child.path, name=child.name,
                                            nested_tf_module=child_source_module_object_copy,
                                            foreach_idx=child.for_each_index)
                self._update_children_foreach_index(original_foreach_or_count_key, original_module_key,
                                                    child_module_key)

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
            ForeachResourceHandler._update_nested_tf_module_foreach_idx(original_foreach_or_count_key, original_module_key,
                                                                        tf_moudle)

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
    def __update_str_attrs(attrs: dict[str, Any], key_to_change: str, val_to_change: str, k: str | int) -> bool:
        if attrs[k] == "${" + key_to_change + "}":
            attrs[k] = val_to_change
            return True
        else:
            attrs[k] = attrs[k].replace("${" + key_to_change + "}", str(val_to_change))
            attrs[k] = attrs[k].replace(key_to_change, str(val_to_change))
            return True

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
    def _build_key_to_val_changes(main_resource: TerraformBlock, new_val: str, new_key: str):
        if main_resource.attributes.get(COUNT_STRING):
            return {COUNT_KEY: new_val}

        return {
            EACH_VALUE: new_val,
            EACH_KEY: new_key
        }

    def _create_new_resource(
            self,
            main_resource: TerraformBlock,
            new_value: int | str,
            resource_idx: int,
            foreach_idx: int,
            new_key: Optional[str] = None,
    ) -> None:
        new_resource = deepcopy(main_resource)
        block_type, block_name = new_resource.name.split('.')
        key_to_val_changes = self._build_key_to_val_changes(main_resource, new_value, new_key)
        config_attrs = new_resource.config.get(block_type, {}).get(block_name, {})

        self._update_foreach_attrs(config_attrs, key_to_val_changes, new_resource)
        idx_to_change = new_key or new_value
        self._add_index_to_resource_block_properties(new_resource, idx_to_change)
        if foreach_idx == 0:
            self.local_graph.vertices[resource_idx] = new_resource
        else:
            self.local_graph.vertices.append(new_resource)

    def _update_foreach_attrs(self, config_attrs: dict[str, Any], key_to_val_changes: [dict[str, Any]],
                              new_resource: TerraformBlock) -> None:
        self._pop_foreach_attrs(new_resource.attributes)
        self._pop_foreach_attrs(config_attrs)
        self._update_attributes(new_resource.attributes, key_to_val_changes)
        foreach_attrs = self._update_attributes(config_attrs, key_to_val_changes)
        new_resource.foreach_attrs = foreach_attrs

    def _create_new_module(
            self,
            main_resource: TerraformBlock,
            new_value: int | str,
            resource_idx: int,
            foreach_idx: int,
            new_key: Optional[str] = None) -> None:
        new_resource = deepcopy(main_resource)
        block_name = new_resource.name
        config_attrs = new_resource.config.get(block_name, {})
        key_to_val_changes = self._build_key_to_val_changes(main_resource, new_value, new_key)
        self._update_foreach_attrs(config_attrs, key_to_val_changes, new_resource)
        idx_to_change = new_key or new_value
        new_resource.for_each_index = idx_to_change

        main_resource_module_key = TFModule(
            path=new_resource.path,
            name=main_resource.name,
            nested_tf_module=new_resource.source_module_object,
        )

        # Without making this copy the test don't pass, as we might access the data structure in the middle of an update
        copy_of_vertices_by_module_dependency = deepcopy(self.local_graph.vertices_by_module_dependency)
        main_resource_module_value = deepcopy(copy_of_vertices_by_module_dependency[main_resource_module_key])
        new_resource_module_key = TFModule(new_resource.path, new_resource.name, new_resource.source_module_object,
                                           idx_to_change)

        self._update_block_name_and_id(new_resource, idx_to_change)
        self._update_resolved_entry_for_tf_definition(new_resource, idx_to_change, main_resource_module_key)
        if foreach_idx != 0:
            self.local_graph.vertices.append(new_resource)
            self._create_new_module_with_vertices(main_resource, main_resource_module_value, resource_idx, new_resource,
                                                  new_resource_module_key)
        else:
            self.local_graph.vertices[resource_idx] = new_resource

            key_with_foreach_index = deepcopy(main_resource_module_key)
            key_with_foreach_index.foreach_idx = idx_to_change
            self.local_graph.vertices_by_module_dependency[key_with_foreach_index] = main_resource_module_value

        del copy_of_vertices_by_module_dependency, new_resource, main_resource_module_key, main_resource_module_value

    def _create_new_module_with_vertices(self, main_resource: TerraformBlock, main_resource_module_value: dict[str, list[int]],
                                         resource_idx: Any, new_resource: TerraformBlock | None = None,
                                         new_resource_module_key: TFModule | None = None) -> None:
        if new_resource is None:
            new_resource = deepcopy(main_resource)
            new_resource_module_key = TFModule(new_resource.path, new_resource.name, new_resource.source_module_object,
                                               new_resource.for_each_index)

        new_resource_vertex_idx = len(self.local_graph.vertices) - 1
        original_vertex_source_module = self.local_graph.vertices[resource_idx].source_module_object
        if original_vertex_source_module:
            source_module_key = TFModule(
                path=original_vertex_source_module.path,
                name=original_vertex_source_module.name,
                nested_tf_module=original_vertex_source_module.nested_tf_module,
            )
        else:
            source_module_key = None
        self.local_graph.vertices_by_module_dependency[source_module_key][BlockType.MODULE].append(new_resource_vertex_idx)
        new_vertices_module_value = self._add_new_vertices_for_module(new_resource_module_key,
                                                                      main_resource_module_value,
                                                                      new_resource_vertex_idx)
        self.local_graph.vertices_by_module_dependency.update({new_resource_module_key: new_vertices_module_value})

    def _add_new_vertices_for_module(self, new_module_key: TFModule, new_module_value: dict[str, list[int]],
                                     new_resource_vertex_idx: int) -> dict[str: list[int]]:
        new_vertices_module_value: dict[str: list[int]] = defaultdict(list)
        for vertex_type, vertices_idx in new_module_value.items():
            for vertex_idx in vertices_idx:
                module_vertex = self.local_graph.vertices[vertex_idx]
                new_vertex = deepcopy(module_vertex)
                new_vertex.source_module_object = new_module_key
                self.local_graph.vertices.append(new_vertex)

                # Update source module based on the new added vertex
                new_vertex.source_module.pop()
                new_vertex.source_module.add(new_resource_vertex_idx)

                new_vertex_idx = len(self.local_graph.vertices) - 1
                new_vertices_module_value[vertex_type].append(new_vertex_idx)

                if vertex_type == BlockType.MODULE:
                    module_vertex_key = TFModule(path=module_vertex.path, name=module_vertex.name,
                                                 nested_tf_module=module_vertex.source_module_object,
                                                 foreach_idx=module_vertex.for_each_index)
                    module_vertex_value = self.local_graph.vertices_by_module_dependency[module_vertex_key]
                    self._create_new_module_with_vertices(new_vertex, module_vertex_value, new_vertex_idx)

        return new_vertices_module_value

    def _create_new_resources_foreach(self, statement: list[str] | dict[str, Any], block_idx: int) -> None:
        main_resource = self.local_graph.vertices[block_idx]
        if isinstance(statement, list):
            for i, new_value in enumerate(statement):
                self._create_new_foreach_resource(block_idx, i, main_resource, new_key=new_value, new_value=new_value)
        if isinstance(statement, dict):
            for i, (new_key, new_value) in enumerate(statement.items()):
                self._create_new_foreach_resource(block_idx, i, main_resource, new_key, new_value)
        if main_resource.block_type == BlockType.MODULE:
            if isinstance(statement, list):
                for i, new_value in enumerate(statement):
                    should_override = True if i == 0 else False
                    self._update_module_children(main_resource, new_value, should_override_foreach_key=should_override)
            elif isinstance(statement, dict):
                for i, (new_key, _) in enumerate(statement.items()):
                    should_override = True if i == 0 else False
                    self._update_module_children(main_resource, new_key, should_override_foreach_key=should_override)

    def _create_new_foreach_resource(self, block_idx: int, foreach_idx: int, main_resource: TerraformBlock,
                                     new_key: int | str, new_value: int | str) -> None:
        if main_resource.block_type == BlockType.MODULE:
            self._create_new_module(main_resource, new_value, new_key=new_key, resource_idx=block_idx,
                                    foreach_idx=foreach_idx)
        elif main_resource.block_type == BlockType.RESOURCE:
            self._create_new_resource(main_resource, new_value, new_key=new_key, resource_idx=block_idx,
                                      foreach_idx=foreach_idx)

    @staticmethod
    def _add_index_to_resource_block_properties(block: TerraformBlock, idx: str | int) -> None:
        block_type, block_name = block.name.split('.')
        idx_with_separator = ForeachResourceHandler._update_block_name_and_id(block, idx)
        if block.config.get(block_type) and block.config.get(block_type, {}).get(block_name):
            block.config[block_type][f"{block_name}[{idx_with_separator}]"] = block.config[block_type].pop(block_name)

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

    def _create_new_resources(self, block_index_to_statement: FOR_EACH_BLOCK_TYPE) -> None:
        for block_idx, statement in block_index_to_statement.items():
            if not statement:
                continue
            if isinstance(statement, int):
                self._create_new_resources_count(statement, block_idx)
            else:
                self._create_new_resources_foreach(statement, block_idx)

