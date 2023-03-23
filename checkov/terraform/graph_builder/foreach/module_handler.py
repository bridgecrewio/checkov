import itertools
from copy import deepcopy
from typing import Any

from checkov.terraform import TFModule
from checkov.terraform.graph_builder.foreach.consts import FOREACH_STRING, COUNT_STRING
from checkov.terraform.graph_builder.foreach.handler import ForeachResourceHandler
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph


class ForeachModuleHandler(ForeachResourceHandler):
    def __init__(self, local_graph: TerraformLocalGraph):
        super().__init__(local_graph)

    def _handle_foreach_rendering_for_module(self, modules_blocks: list[int]) -> None:
        """
        modules_blocks (list[int]): list of module blocks indexes in the graph that contains for_each / counts.
        """
        if not modules_blocks:
            return
        current_level = [None]
        main_module_modules = deepcopy(self.local_graph.vertices_by_module_dependency.get(None)[BlockType.MODULE])
        modules_to_render = main_module_modules

        # TODO add documentation on logic here + Move the render graph to here
        while modules_to_render:
            for module_idx in modules_to_render:
                module_block = self.local_graph.vertices[module_idx]
                for_each = module_block.attributes.get(FOREACH_STRING)
                count = module_block.attributes.get(COUNT_STRING)
                sub_graph = self._build_sub_graph(modules_blocks)
                self._render_sub_graph(sub_graph, blocks_to_render=modules_blocks)
                if for_each:
                    for_each = self._handle_static_statement(module_idx, sub_graph)
                    if not self._is_static_statement(module_idx, sub_graph):
                        continue
                    self.duplicate_module_with_for_each(module_idx, for_each)
                elif count:
                    count = self._handle_static_statement(module_idx, sub_graph)
                    if not self._is_static_statement(module_idx, sub_graph):
                        continue
                    self.duplicate_module_with_count(module_idx, count)
            modules_to_render = self._get_modules_to_render(current_level)

    def duplicate_module_with_for_each(self, module_idx: int, for_each: dict[str, Any] | list[str]) -> None:
        self._create_new_resources_foreach(for_each, module_idx)

    def duplicate_module_with_count(self, module_idx: int, count: int) -> None:
        self._create_new_resources_count(count, module_idx)

    def _get_modules_to_render(self, current_level: list[TFModule | None]):
        rendered_modules = [self.local_graph.vertices_by_module_dependency[curr]['module'] for curr in current_level][0]
        current_level.clear()
        for m_idx in rendered_modules:
            m = self.local_graph.vertices[m_idx]
            m_name = m.name.split('[')[0]
            current_level.append(TFModule(m.path, m_name, m.source_module_object, m.for_each_index))
        modules_to_render = [self.local_graph.vertices_by_module_dependency[curr]['module'] for curr in current_level]
        return list(itertools.chain.from_iterable(modules_to_render))
