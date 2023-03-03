from __future__ import annotations

import logging
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.github_actions.graph_builder.graph_components.resource_types import ResourceType
from checkov.github_actions.utils import get_scannable_file_paths, parse_file


class GitHubActionsLocalGraph(ObjectLocalGraph):
    def __init__(self, definitions: dict[str | Path, dict[str, Any] | list[dict[str, Any]]]) -> None:
        super().__init__(definitions=definitions)

        self.source = GraphSource.GITHUB_ACTIONS
        self.job_steps_map: "dict[tuple[str, str], list[tuple[str, str]]]" = defaultdict(list)

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            if not isinstance(definition, dict):
                logging.debug(f"definition of file {file_path} has the wrong type {type(definition)}")
                return

            file_path = str(file_path)

            self._create_jobs_vertices(file_path=file_path, jobs=definition.get(ResourceType.JOBS))
            self._create_steps_vertices(file_path=file_path, jobs=definition.get(ResourceType.JOBS))
            self._create_permissions_vertices(file_path=file_path, permissions=definition.get(ResourceType.PERMISSIONS))
            self._create_on_vertices(file_path=file_path, on=definition.get(ResourceType.ON))

    def _create_jobs_vertices(self, file_path: str, jobs: Any) -> None:
        """Creates jobs vertices"""

        if not jobs or not isinstance(jobs, dict):
            return

        for name, config in jobs.items():
            if name in (START_LINE, END_LINE):
                continue

            attributes = deepcopy(config)
            attributes[CustomAttributes.RESOURCE_TYPE] = ResourceType.JOBS

            block_name = f"{ResourceType.JOBS}.{name}"

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

    def _create_steps_vertices(self, file_path: str, jobs: Any) -> None:
        """Creates steps vertices from jobs"""

        if not jobs or not isinstance(jobs, dict):
            return

        for name, job_config in jobs.items():
            if name in (START_LINE, END_LINE):
                continue

            steps = job_config.get(ResourceType.STEPS)

            if not steps or not isinstance(steps, list):
                continue

            for idx, config in enumerate(steps):
                if not isinstance(config, dict):
                    # should not happen
                    continue

                attributes = deepcopy(config)
                attributes[CustomAttributes.RESOURCE_TYPE] = ResourceType.STEPS

                block_name = f"{ResourceType.JOBS}.{name}.{ResourceType.STEPS}.{idx + 1}"

                block = Block(
                    name=block_name,
                    config=config,
                    path=file_path,
                    block_type=BlockType.RESOURCE,
                    attributes=attributes,
                    id=block_name,
                    source=self.source,
                )
                self.vertices.append(block)
                self.job_steps_map[(file_path, f"{ResourceType.JOBS}.{name}")].append((file_path, block_name))

    def _create_permissions_vertices(self, file_path: str, permissions: Any) -> None:
        """Creates root-level permissions vertices"""

        if permissions is None:
            # if 'permissions' is not set in a file, then it is automatically 'write-all'
            permissions = "write-all"

        if not permissions or not isinstance(permissions, (str, dict)):
            return

        if isinstance(permissions, str):
            # to get the correct line numbers we would need to check the raw definition
            config = {
                "permissions": permissions,
                START_LINE: 0,
                END_LINE: 0,
            }
        else:
            config = {
                "permissions": permissions,
                START_LINE: permissions[START_LINE],
                END_LINE: permissions[END_LINE],
            }

        attributes = deepcopy(config)
        attributes[CustomAttributes.RESOURCE_TYPE] = ResourceType.PERMISSIONS

        block_name = ResourceType.PERMISSIONS

        block = Block(
            name=block_name,
            config=config,
            path=file_path,
            block_type=BlockType.RESOURCE,
            attributes=attributes,
            id=block_name,
            source=self.source,
        )
        self.vertices.append(block)

    def _create_on_vertices(self, file_path: str, on: Any) -> None:
        if not on:
            return

        if isinstance(on, (str, list)):
            # to get the correct line numbers we would need to check the raw definition
            config: "dict[str, Any]" = {
                "on": on,
                START_LINE: 0,
                END_LINE: 0,
            }
        elif isinstance(on, dict):
            config = {
                "on": on,
                START_LINE: on[START_LINE],
                END_LINE: on[END_LINE],
            }
        else:
            return

        attributes = deepcopy(config)
        attributes[CustomAttributes.RESOURCE_TYPE] = ResourceType.ON

        block_name = ResourceType.ON

        block = Block(
            name=block_name,
            config=config,
            path=file_path,
            block_type=BlockType.RESOURCE,
            attributes=attributes,
            id=block_name,
            source=self.source,
        )
        self.vertices.append(block)

    def _create_edges(self) -> None:
        self._create_jobs_to_steps_edges()

    def _create_jobs_to_steps_edges(self) -> None:
        """Creates edges from jobs to steps"""

        if not self.job_steps_map:
            return

        for path_and_name, path_and_steps in self.job_steps_map.items():
            origin_vertex_index = self.vertices_by_path_and_name[path_and_name]

            for path_and_step_name in path_and_steps:
                dest_vertex_index = self.vertices_by_path_and_name[path_and_step_name]

                self._create_edge(
                    origin_vertex_index=origin_vertex_index,
                    dest_vertex_index=dest_vertex_index,
                )

    @staticmethod
    def get_files_definitions(root_folder: str | Path) -> dict[str | Path, dict[str, Any] | list[dict[str, Any]]]:
        definitions: "dict[str | Path, dict[str, Any] | list[dict[str, Any]]]" = {}
        file_paths = get_scannable_file_paths(root_folder=root_folder)

        for file_path in file_paths:
            result = parse_file(f=file_path)
            if result is not None:
                definitions[file_path] = result[0]

        return definitions
