from __future__ import annotations

from typing import Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.local_graph import LocalGraph, _Block
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.serverless.graph_builder.graph_components.blocks import ServerlessBlock
from checkov.serverless.utils import ServerlessElements


class ServerlessLocalGraph(LocalGraph[ServerlessBlock]):
    def __init__(self, definitions: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.vertices: list[ServerlessBlock] = []
        self.definitions = definitions
        self.vertices_by_path_and_id: dict[tuple[str, str], int] = {}
        self.vertices_by_name: dict[str, int] = {}

    def build_graph(self, render_variables: bool = True) -> None:
        self._create_vertices()

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            self._create_params_vertices(file_path=file_path, params_node=definition.get(ServerlessElements.PARAMS))
            self._create_provider_vertices(file_path=file_path, providers_node=definition.get(ServerlessElements.PROVIDER))
            self._create_functions_vertices(file_path=file_path,
                                            functions_node=definition.get(ServerlessElements.FUNCTIONS))
            self._create_layers_vertices(file_path=file_path, layers=definition.get(ServerlessElements.LAYERS))
            self._create_custom_vertices(file_path=file_path, customs=definition.get(ServerlessElements.CUSTOM))
            self._create_package_vertices(file_path=file_path, packages=definition.get(ServerlessElements.PACKAGE))
            self._create_plugins_vertices(file_path=file_path, plugins=definition.get(ServerlessElements.PLUGINS))
            self._create_service_vertices(file_path=file_path, services=definition.get(ServerlessElements.SERVICE))
            self._create_resources_vertices(file_path=file_path, resources=definition.get(ServerlessElements.RESOURCES))


        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_by_path_and_id[(vertex.path, vertex.id)] = i

            self.in_edges[i] = []
            self.out_edges[i] = []

    def _create_params_vertices(self, file_path: str, params_node: dict[str, dict[str, Any]] | None) -> None:
        if not params_node:
            return

        for param_name, param_config in params_node.items():
            resource_type = ServerlessElements.PARAMS

            attributes = pickle_deepcopy(param_config)
            attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

            # Create a Param vertex
            self.vertices.append(ServerlessBlock(
                name=f'{file_path}.{param_name}',
                config=param_config,
                path=file_path,
                block_type=resource_type,
                attributes=attributes,
                id=f"{file_path}.{resource_type}.{param_name}"
            ))

    def _create_provider_vertices(self, file_path: str, providers_node: dict[str, dict[str, Any]] | None) -> None:
        pass

    def _create_functions_vertices(self, file_path: str, functions_node: dict[str, Any] | list[str, Any] | None) -> None:
        if not functions_node:
            return

        for function in functions_node:
            config = functions_node[function]
            if not isinstance(config, dict):
                continue

            resource_type = ServerlessElements.FUNCTIONS

            attributes = pickle_deepcopy(config)
            attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

            self.vertices.append(
                ServerlessBlock(
                    name=f'{file_path}.{function}',
                    config=config,
                    path=file_path,
                    block_type=resource_type,
                    attributes=attributes,
                    id=f"{file_path}.{resource_type}.{function}"
                )
            )

    def _create_layers_vertices(self, file_path: str, layers: dict[str, dict[str, Any]] | None) -> None:
        if not layers:
            return

        for layer in layers:
            config = layers[layer]
            if not isinstance(config, dict):
                continue

            resource_type = ServerlessElements.FUNCTIONS

            attributes = pickle_deepcopy(config)
            attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

            self.vertices.append(
                ServerlessBlock(
                    name=f'{file_path}.{layer}',
                    config=config,
                    path=file_path,
                    block_type=resource_type,
                    attributes=attributes,
                    id=f"{file_path}.{resource_type}.{layer}"
                )
            )

    def _create_custom_vertices(self, file_path: str, customs: dict[str, dict[str, Any]] | None) -> None:
        pass

    def _create_package_vertices(self, file_path: str, packages: dict[str, dict[str, Any]] | None) -> None:
        pass

    def _create_plugins_vertices(self, file_path: str, plugins: dict[str, dict[str, Any]] | None) -> None:
        pass

    def _create_service_vertices(self, file_path: str, services: dict[str, dict[str, Any]] | None) -> None:
        pass

    def _create_resources_vertices(self, file_path: str, resources: dict[str, dict[str, Any]] | None) -> None:
        pass

    def get_resources_types_in_graph(self) -> list[str]:
        # not used
        return []

    @staticmethod
    def update_vertex_config(vertex: _Block, changed_attributes: list[str] | dict[str, Any],
                             has_dynamic_blocks: bool = False) -> None:
        pass

    def update_vertices_configs(self) -> None:
        pass




