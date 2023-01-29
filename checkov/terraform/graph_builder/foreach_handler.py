from __future__ import annotations
import re
from typing import Any

from checkov.terraform.graph_builder.graph_components.blocks import TerraformBlock
from checkov.terraform.graph_builder.variable_rendering.evaluate_terraform import evaluate_terraform

RESOURCE_STRING = 'resource'
MODULE_STRING = 'module'


def handle_foreach_rendering(foreach_blocks: dict[str, list[TerraformBlock]]):
    handle_foreach_rendering_for_resource(foreach_blocks.get(RESOURCE_STRING))
    # handle_foreach_rendering_for_module(foreach_blocks.get(MODULE_STRING))


def handle_foreach_rendering_for_resource(resources_blocks: list[TerraformBlock]):
    # old_resources_to_delete_edges: list[TerraformBlock] = []
    # new_resource_to_create_edges: list[TerraformBlock] = []
    for tf_block in resources_blocks:
        render_foreach_resource(tf_block)
        # old_resources_to_delete_edges.append(tf_block)
        # new_resource_to_create_edges.extend(create_new_foreach_resources(tf_block))
    # delete_edges_from_old_resource(old_resources_to_delete_edges)
    # create_edges_for_new_foreach_resources(new_resource_to_create_edges)


def render_foreach_resource(block: TerraformBlock):
    foreach_statement = evaluate_terraform(block.attributes.get("for_each", [""]))
    if isinstance(foreach_statement, list) and len(foreach_statement) == 1:
        foreach_statement = foreach_statement[0]
    if not should_render_for_each(foreach_statement):
        block.attributes['foreach_value'] = foreach_statement


def should_render_for_each(foreach_statement: str | set[str] | list[str] | dict[str, Any]) -> bool:
    '''
    foreach statement can be list/map of strings or map, if its string we need to render it for sure.
    '''
    return isinstance(foreach_statement, str) and re.search(r"(var|module|local)\.", foreach_statement)


def create_new_foreach_resources(block: TerraformBlock) -> list[TerraformBlock]:
    pass


def delete_edges_from_old_resource(block: list[TerraformBlock]):
    pass


def create_edges_for_new_foreach_resources(blocks: list[TerraformBlock]):
    pass


def handle_foreach_rendering_for_module(modules_blocks: list[TerraformBlock]):
    pass
