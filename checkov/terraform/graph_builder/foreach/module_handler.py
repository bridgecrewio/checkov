from __future__ import annotations

import itertools
import typing
from collections import defaultdict
from typing import Any
import json

from checkov.common.util.consts import RESOLVED_MODULE_ENTRY_NAME
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.terraform import TFModule, TFDefinitionKey
from checkov.terraform.graph_builder.foreach.abstract_handler import ForeachAbstractHandler
from checkov.terraform.graph_builder.foreach.consts import FOREACH_STRING, COUNT_STRING
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock

if typing.TYPE_CHECKING:
    from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachModuleHandler(ForeachAbstractHandler):
    def __init__(self, local_graph: TerraformLocalGraph):
        super().__init__(local_graph)

    def handle(self, modules_blocks: list[int]) -> None:
        """
        modules_blocks (list[int]): list of module blocks indexes in the graph that contains for_each / counts.
        """
        if not modules_blocks:
            return
        current_level: list[TFModule | None] = [None]
        # We use `[:]` instead of deepcopy as it's much faster and the list has only primitive types (int indexes)
        main_module_modules = self.local_graph.vertices_by_module_dependency[None][BlockType.MODULE][:]
        modules_to_render = main_module_modules

        while modules_to_render:
            modules_to_render = self._render_foreach_modules_by_levels(modules_blocks, modules_to_render, current_level)
            self.local_graph._arrange_graph_data()
            self.local_graph._build_edges()

    def _render_foreach_modules_by_levels(self, modules_blocks: list[int], modules_to_render: list[int],
                                          current_level: list[TFModule | None]) -> list[int]:
        """
        modules_blocks: The module blocks with for_each/count statement in the graph.
        modules_to_render: The list of modules indexes to render at this iteration.
        current_level: The parent current level that we are running on this iteration (first will be None).

        return: the next (list) of the modules to render.

        For example: at this folder - tests/terraform/graph/variable_rendering/resources/foreach_module_dup_foreach
        We will run over the levels by:
        First level -> s3_module and s3_module2 (Copying the module and all his dependencies)
        Second level -> inner_s3_module and inner_s3_module2 (Copying the module and all his dependencies)
        This will generate a graph with 20 modules and 16 resources.
        """
        sub_graph = self._build_sub_graph(modules_blocks)
        self._render_sub_graph(sub_graph, blocks_to_render=modules_blocks)
        for module_idx in modules_to_render:
            module_block = self.local_graph.vertices[module_idx]
            for_each = module_block.attributes.get(FOREACH_STRING)
            count = module_block.attributes.get(COUNT_STRING)
            if for_each:
                for_each = self._handle_static_statement(module_idx, sub_graph)
                if not for_each or not self._is_static_statement(module_idx, sub_graph):
                    continue
                if isinstance(for_each, (list, dict)):
                    self._duplicate_module_with_for_each(module_idx, for_each)
            elif count:
                count = self._handle_static_statement(module_idx, sub_graph)
                if not count or not self._is_static_statement(module_idx, sub_graph):
                    continue
                if isinstance(count, int):
                    self._duplicate_module_with_count(module_idx, count)
        return self._get_modules_to_render(current_level)

    def _duplicate_module_with_for_each(self, module_idx: int, for_each: dict[str, Any] | list[str]) -> None:
        self._create_new_resources_foreach(for_each, module_idx)

    def _duplicate_module_with_count(self, module_idx: int, count: int) -> None:
        self._create_new_resources_count(count, module_idx)

    def _get_rendered_modules(self, source_modules: list[TFModule | None]) -> list[int]:
        """
        Returns a list of module indexes that have been rendered in the current iteration.
        """
        modules_created_by_provided_source_packed = [self.local_graph.vertices_by_module_dependency[curr][BlockType.MODULE] for curr in source_modules]
        modules_created_by_provided_source = list(itertools.chain(*modules_created_by_provided_source_packed))  # list of lists -> single list
        return modules_created_by_provided_source

    def _get_modules_to_render(self, current_level: list[TFModule | None]) -> list[int]:
        rendered_modules = self._get_rendered_modules(current_level)
        current_level.clear()
        for m_idx in rendered_modules:
            current_level.append(self._get_current_tf_module_object(m_idx))
        modules_to_render = [self.local_graph.vertices_by_module_dependency[curr][BlockType.MODULE] for curr in current_level]
        return list(itertools.chain.from_iterable(modules_to_render))

    def _get_current_tf_module_object(self, m_idx: int) -> TFModule:
        m = self.local_graph.vertices[m_idx]
        m_name = m.name.split('[')[0]
        return TFModule(m.path, m_name, m.source_module_object, m.for_each_index)

    def _create_new_resources_foreach(self, statement: list[str] | dict[str, Any], block_idx: int) -> None:
        # Important it will be before the super call to avoid changes occurring from super
        main_resource = self.local_graph.vertices[block_idx]
        super()._create_new_resources_foreach(statement, block_idx)

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
        self._create_new_module(main_resource, new_value, new_key=new_key, resource_idx=block_idx,
                                foreach_idx=foreach_idx)

    def _update_module_children(self, main_resource: TerraformBlock,
                                original_foreach_or_count_key: int | str,
                                should_override_foreach_key: bool = True) -> None:
        foreach_idx = original_foreach_or_count_key if not should_override_foreach_key else None
        original_module_key = TFModule(path=main_resource.path, name=main_resource.name,
                                       nested_tf_module=main_resource.source_module_object, foreach_idx=foreach_idx)
        self._update_children_foreach_index(original_foreach_or_count_key, original_module_key,
                                            should_override_foreach_key=should_override_foreach_key)

    def _create_new_resources_count(self, statement: int, block_idx: int) -> None:
        main_resource = self.local_graph.vertices[block_idx]
        for i in range(statement):
            self._create_new_module(main_resource, i, resource_idx=block_idx, foreach_idx=i)

        # We purposely do it at the end to avoid influencing data structures in the middle of an update
        for i in range(statement):
            should_override = True if i == 0 else False
            self._update_module_children(main_resource, i, should_override_foreach_key=should_override)

    def _update_children_foreach_index(self, original_foreach_or_count_key: int | str, original_module_key: TFModule,
                                       current_module_key: TFModule | None = None,
                                       should_override_foreach_key: bool = True) -> None:
        """
        Go through all child vertices and update source_module_object with foreach_idx
        """
        if current_module_key is None:
            current_module_key = original_module_key
        if current_module_key not in self.local_graph.vertices_by_module_dependency:
            # Make sure we check both the intended key (with foreach key) and the one without the foreach key.
            # This is important as we have some iterations in which we try to access with the intended key before
            # we actually updated the dict itself
            nullified_key = self._get_tf_module_with_no_foreach(current_module_key)
            if nullified_key not in self.local_graph.vertices_by_module_dependency:
                return
            current_module_key = nullified_key
        values = self.local_graph.vertices_by_module_dependency[current_module_key].values()
        for child_indexes in values:
            for child_index in child_indexes:
                child = self.local_graph.vertices[child_index]

                child.source_module_object = self._get_module_with_only_relevant_foreach_idx(
                    original_foreach_or_count_key, original_module_key, child.source_module_object)
                self._update_resolved_entry_for_tf_definition(child, original_foreach_or_count_key, original_module_key)

                # Important to copy to avoid changing the object by reference
                child_source_module_object_copy = pickle_deepcopy(child.source_module_object)
                if should_override_foreach_key and child_source_module_object_copy is not None:
                    child_source_module_object_copy = self._get_tf_module_with_no_foreach(
                        child_source_module_object_copy)

                child_module_key = TFModule(path=child.path, name=child.name,
                                            nested_tf_module=child_source_module_object_copy,
                                            foreach_idx=child.for_each_index)
                del child_source_module_object_copy
                self._update_children_foreach_index(original_foreach_or_count_key, original_module_key,
                                                    child_module_key)

    @staticmethod
    def _get_tf_module_with_no_foreach(original_module: TFModule | None) -> TFModule | None:
        if original_module is None:
            return original_module
        return TFModule(name=original_module.name, path=original_module.path, foreach_idx=None,
                        nested_tf_module=ForeachModuleHandler._get_tf_module_with_no_foreach(
                            original_module.nested_tf_module))

    def _create_new_module(
            self,
            main_resource: TerraformBlock,
            new_value: int | str,
            resource_idx: int,
            foreach_idx: int,
            new_key: int | str | None = None) -> None:
        new_resource = pickle_deepcopy(main_resource)
        block_name = new_resource.name
        config_attrs = new_resource.config.get(block_name, {})
        key_to_val_changes = self._build_key_to_val_changes(main_resource, new_value, new_key)
        self._update_foreach_attrs(config_attrs, key_to_val_changes, new_resource)
        idx_to_change = new_key or new_value
        new_resource.for_each_index = idx_to_change

        main_resource_module_key = TFModule(
            path=new_resource.path,
            name=main_resource.name,
            nested_tf_module=new_resource.source_module_object
        )

        # Without making this copy the test don't pass, as we might access the data structure in the middle of an update
        copy_of_vertices_by_module_dependency = pickle_deepcopy(self.local_graph.vertices_by_module_dependency)
        main_resource_module_value = pickle_deepcopy(copy_of_vertices_by_module_dependency[main_resource_module_key])
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

            key_with_foreach_index = TFModule(name=main_resource_module_key.name,
                                              path=main_resource_module_key.path,
                                              nested_tf_module=main_resource_module_key.nested_tf_module,
                                              foreach_idx=idx_to_change)
            self.local_graph.vertices_by_module_dependency[key_with_foreach_index] = main_resource_module_value
            self.local_graph.vertices_by_module_dependency_by_name[key_with_foreach_index][new_resource.name] = main_resource_module_value

        del copy_of_vertices_by_module_dependency, new_resource, main_resource_module_key, main_resource_module_value

    def _create_new_module_with_vertices(self, main_resource: TerraformBlock,
                                         main_resource_module_value: dict[str, list[int]],
                                         resource_idx: Any, new_resource: TerraformBlock | None = None,
                                         new_resource_module_key: TFModule | None = None) -> None:
        if new_resource is None:
            new_resource_name = main_resource.name
            new_resource_module_key = TFModule(main_resource.path, new_resource_name, main_resource.source_module_object,
                                               main_resource.for_each_index)
        else:
            new_resource_name = new_resource.name

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
        self.local_graph.vertices_by_module_dependency_by_name[source_module_key][BlockType.MODULE][new_resource_name].append(new_resource_vertex_idx)
        new_vertices_module_value = self._add_new_vertices_for_module(new_resource_module_key, main_resource_module_value, new_resource_vertex_idx)
        self.local_graph.vertices_by_module_dependency.update({new_resource_module_key: new_vertices_module_value})
        self.local_graph.vertices_by_module_dependency_by_name.update({new_resource_module_key: {new_resource_name: new_vertices_module_value}})

    def _add_new_vertices_for_module(self, new_module_key: TFModule | None, new_module_value: dict[str, list[int]],
                                     new_resource_vertex_idx: int) -> dict[str, list[int]]:
        new_vertices_module_value: dict[str, list[int]] = defaultdict(list)
        seen_vertices = []
        for vertex_type, vertices_idx in new_module_value.items():
            for vertex_idx in vertices_idx:
                module_vertex = self.local_graph.vertices[vertex_idx]
                if module_vertex in seen_vertices:
                    # Makes sure we won't mistakenly go over vertices we already copied.
                    # This may happen when using nested modules with count>2,
                    # as we might duplicate the previous count index resources mistakenly.
                    # See issue https://github.com/bridgecrewio/checkov/issues/6068
                    continue
                seen_vertices.append(module_vertex)
                new_vertex = pickle_deepcopy(module_vertex)
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

    @staticmethod
    def _update_resolved_entry_for_tf_definition(child: TerraformBlock, original_foreach_or_count_key: int | str,
                                                 original_module_key: TFModule) -> None:
        if child.block_type == BlockType.RESOURCE:
            child_name, child_type = child.name.split('.')
            config = child.config[child_name][child_type]
        else:
            config = child.config.get(child.name)
        if isinstance(config, dict):
            resolved_module_name = config.get(RESOLVED_MODULE_ENTRY_NAME)
            if resolved_module_name is not None and len(resolved_module_name) > 0:
                # iterate over each item in the resolved list and override it with updated data
                for idx, original_definition_key in enumerate(resolved_module_name):
                    if isinstance(original_definition_key, str):
                        original_definition_key = TFDefinitionKey.from_json(json.loads(original_definition_key))
                    resolved_tf_source_module = TFDefinitionKey.from_json(json.loads(resolved_module_name[idx])) if isinstance(resolved_module_name[idx], str) else resolved_module_name[idx]
                    tf_source_modules = ForeachModuleHandler._get_module_with_only_relevant_foreach_idx(
                        original_foreach_or_count_key,
                        original_module_key,
                        resolved_tf_source_module.tf_source_modules,
                    )
                    resolved_module_name[idx] = TFDefinitionKey(file_path=original_definition_key.file_path,
                                                                tf_source_modules=tf_source_modules)

    @staticmethod
    def _get_module_with_only_relevant_foreach_idx(original_foreach_or_count_key: int | str,
                                                   original_module_key: TFModule,
                                                   tf_moudle: TFModule | None) -> TFModule | None:
        if tf_moudle is None:
            return None
        if tf_moudle == original_module_key:
            return TFModule(name=tf_moudle.name, path=tf_moudle.path,
                            nested_tf_module=tf_moudle.nested_tf_module,
                            foreach_idx=original_foreach_or_count_key)
        nested_module = tf_moudle.nested_tf_module
        updated_module = ForeachModuleHandler._get_module_with_only_relevant_foreach_idx(
            original_foreach_or_count_key, original_module_key, nested_module)
        return TFModule(name=tf_moudle.name, path=tf_moudle.path,
                        nested_tf_module=updated_module,
                        foreach_idx=tf_moudle.foreach_idx)
