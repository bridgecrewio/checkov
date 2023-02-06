from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource, SELF_REFERENCE
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.ansible.graph_builder.graph_components.resource_types import ResourceType
from checkov.ansible.utils import get_scannable_file_paths, TASK_RESERVED_KEYWORDS, parse_file


class AnsibleLocalGraph(ObjectLocalGraph):
    def __init__(self, definitions: dict[str | Path, dict[str, Any] | list[dict[str, Any]]]) -> None:
        super().__init__(definitions=definitions)

        self.source = GraphSource.ANSIBLE

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            if not isinstance(definition, list):
                logging.debug(f"definition of file {file_path} has the wrong type {type(definition)}")
                continue

            file_path = str(file_path)

            for code_block in definition:
                if ResourceType.TASKS in code_block:
                    for task in code_block[ResourceType.TASKS]:
                        self._process_blocks(file_path=file_path, task=task)
                else:
                    self._process_blocks(file_path=file_path, task=code_block)

    def _process_blocks(self, file_path: str, task: Any) -> None:
        """Checks for possible block usage"""

        if not task or not isinstance(task, dict):
            return

        if "block" in task and isinstance(task["block"], list):
            self._create_block_vertices(file_path=file_path, block=task)

            for block_task in task["block"]:
                self._create_tasks_vertices(file_path=file_path, task=block_task)
        else:
            self._create_tasks_vertices(file_path=file_path, task=task)

    def _create_tasks_vertices(self, file_path: str, task: Any) -> None:
        """Creates tasks vertices"""

        if not task or not isinstance(task, dict):
            return

        # grab the task name at the beginning before trying to find the actual module name
        task_name = task.get("name") or "unknown"

        for name, config in task.items():
            if name in TASK_RESERVED_KEYWORDS:
                continue
            if name in (START_LINE, END_LINE):
                continue

            resource_type = f"{ResourceType.TASKS}.{name}"
            block_name = f"{resource_type}.{task_name}"

            if isinstance(config, str):
                # this happens when modules have no parameters and are directly used with the user input
                # ex. ansible.builtin.command: cat /etc/passwd
                config = {SELF_REFERENCE: config}

            attributes = deepcopy(config)
            attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

            # only the module code is relevant for validation,
            # but in the check result the whole task should be visible
            attributes[START_LINE] = task[START_LINE]
            attributes[END_LINE] = task[END_LINE]

            self.vertices.append(
                Block(
                    name=block_name,
                    config=config,
                    path=file_path,
                    block_type=BlockType.RESOURCE,
                    attributes=attributes,
                    id=block_name,
                    source=self.source,
                )
            )

            # no need to further check
            break

    def _create_block_vertices(self, file_path: str, block: dict[str, Any]) -> None:
        """Creates block vertices"""

        # grab the block name, if it exists
        block_name = f'{ResourceType.BLOCK}.{block.get("name") or "unknown"}'

        config = block
        attributes = deepcopy(config)
        attributes[CustomAttributes.RESOURCE_TYPE] = ResourceType.BLOCK
        del attributes[ResourceType.BLOCK]  # the real block content are tasks, which have their own vertices

        self.vertices.append(
            Block(
                name=block_name,
                config=config,
                path=file_path,
                block_type=BlockType.RESOURCE,
                attributes=attributes,
                id=block_name,
                source=self.source,
            )
        )

    def _create_edges(self) -> None:
        return None

    @staticmethod
    def get_files_definitions(root_folder: str | Path) -> dict[str | Path, dict[str, Any] | list[dict[str, Any]]]:
        definitions: "dict[str | Path, dict[str, Any] | list[dict[str, Any]]]" = {}
        file_paths = get_scannable_file_paths(root_folder=root_folder)

        for file_path in file_paths:
            result = parse_file(f=file_path)
            if result is not None:
                definitions[file_path] = result[0]

        return definitions
