from __future__ import annotations

from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.local_graph import LocalGraph, _Block
from checkov.common.util.consts import LINE_FIELD_NAMES
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.serverless.graph_builder.graph_components.blocks import ServerlessBlock
from checkov.serverless.utils import ServerlessElements


class ServerlessLocalGraph(LocalGraph[ServerlessBlock]):
    def __init__(self, definitions: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.vertices: list[ServerlessBlock] = []
        self.definitions = definitions
        self.vertices_by_path_and_name: dict[tuple[str, str], int] = {}

    def build_graph(self, render_variables: bool = True) -> None:
        self._create_vertices()

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.FUNCTIONS)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.PARAMS)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.PROVIDER)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.LAYERS)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.CUSTOM)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.PACKAGE)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.PLUGINS)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.SERVICE)
            self._create_vertex(file_path=file_path, definition=definition, element_type=ServerlessElements.RESOURCES)

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_by_path_and_name[(vertex.path, vertex.name)] = i

            self.in_edges[i] = []
            self.out_edges[i] = []

    def _create_vertex(self, file_path: str, definition: dict[str, Any] | None,
                       element_type: ServerlessElements) -> None:
        if not definition:
            return

        resources = definition.get(element_type)

        # resources -> Resources
        if element_type == ServerlessElements.RESOURCES and resources is None:
            resources = definition.get('Resources')

        if isinstance(resources, list) and len(resources) > 0 and \
           isinstance(resources[0], dict) and resources[0]['__file__'] != file_path:
            for r in resources:
                if isinstance(r, dict):
                    self._create_vertex(file_path, {element_type: r}, element_type)
            return

        if not resources:
            return

        elif isinstance(resources, str):
            self.vertices.append(ServerlessBlock(
                name=f'{element_type}',
                config={"value": pickle_deepcopy(resources)},
                path=file_path,
                block_type=element_type,
                attributes={"value": pickle_deepcopy(resources)},
                id=f"{file_path}:{element_type}"
            ))

        else:
            for attribute in resources:
                if isinstance(attribute, str) and attribute in LINE_FIELD_NAMES:
                    continue

                if isinstance(resources, list):
                    full_conf = {"value": pickle_deepcopy(attribute)}
                    self.vertices.append(ServerlessBlock(
                        name=f'{element_type}.{attribute}',
                        config=full_conf,
                        path=file_path,
                        block_type=element_type,
                        attributes=full_conf,
                        id=f"{file_path}:{element_type}.{attribute}"
                    ))

                else:
                    attribute_value = resources[attribute]
                    if not isinstance(attribute_value, dict):
                        full_conf = {"value": pickle_deepcopy(attribute_value)}
                    else:
                        full_conf = attribute_value

                    config = pickle_deepcopy(full_conf)

                    resource_type = element_type

                    attributes = pickle_deepcopy(config)
                    attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

                    self.vertices.append(ServerlessBlock(
                        name=f'{resource_type}.{attribute}',
                        config=config,
                        path=file_path,
                        block_type=resource_type,
                        attributes=attributes,
                        id=f"{file_path}:{resource_type}.{attribute}"
                    ))

    def get_resources_types_in_graph(self) -> list[str]:
        # not used
        return []

    @staticmethod
    def update_vertex_config(vertex: _Block, changed_attributes: list[str] | dict[str, Any],
                             has_dynamic_blocks: bool = False) -> None:
        pass

    def update_vertices_configs(self) -> None:
        pass
