from __future__ import annotations

import logging
import re
from typing import Any, TYPE_CHECKING

from checkov.arm.graph_builder.graph_components.blocks import ArmBlock
from checkov.arm.utils import ArmElements, extract_resource_name_from_resource_id_func, \
    extract_resource_name_from_reference_func
from checkov.arm.graph_builder.variable_rendering.renderer import ArmVariableRenderer
from checkov.arm.graph_builder.graph_components.block_types import BlockType
from checkov.common.graph.graph_builder import CustomAttributes, Edge
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.graph.graph_builder.utils import filter_sub_keys, adjust_value
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.type_forcers import force_int

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.local_graph import Block

DEPENDS_ON_FIELD = 'dependsOn'
RESOURCE_ID_FUNC = 'resourceId('
REFERENCE_FUNC = 'reference('
PARAMETER_FUNC = 'parameters('
VARIABLE_FUNC = 'variables('


class ArmLocalGraph(LocalGraph[ArmBlock]):
    def __init__(self, definitions: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.vertices: list[ArmBlock] = []
        self.definitions = definitions
        self.vertices_by_path_and_id: dict[tuple[str, str], int] = {}
        self.vertices_by_name: dict[str, int] = {}

    def build_graph(self, render_variables: bool = True) -> None:
        self._create_vertices()
        logging.warning(f"[ArmLocalGraph] created {len(self.vertices)} vertices")

        '''
            In order to resolve the resources names for the dependencies we need to render the variables first
            Examples: https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/resource-dependency
        '''

        self._create_vars_and_parameters_edges()
        if render_variables:
            renderer = ArmVariableRenderer(self)
            renderer.render_variables_from_local_graph()
            self._update_resource_vertices_names()

        self._create_edges()
        logging.warning(f"[ArmLocalGraph] created {len(self.edges)} edges")

    def _create_vertices(self) -> None:
        for file_path, definition in self.definitions.items():
            self._create_parameter_vertices(file_path=file_path, parameters=definition.get(ArmElements.PARAMETERS))
            self._create_resource_vertices(file_path=file_path, resources=definition.get(ArmElements.RESOURCES))
            self._create_variables_vertices(file_path=file_path, variables=definition.get(ArmElements.VARIABLES))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
            self.vertices_by_path_and_id[(vertex.path, vertex.id)] = i
            self.vertices_by_name[vertex.name] = i

            self.in_edges[i] = []
            self.out_edges[i] = []

    def _create_variables_vertices(self, file_path: str, variables: dict[str, dict[str, Any]] | None) -> None:
        if not variables:
            return

        for name, conf in variables.items():
            if name in [START_LINE, END_LINE]:
                continue
            if not isinstance(conf, dict) or "value" not in conf:
                full_conf = {"value": pickle_deepcopy(conf)}
            else:
                full_conf = conf
            config = pickle_deepcopy(full_conf)
            attributes = pickle_deepcopy(full_conf)

            self.vertices.append(
                ArmBlock(
                    name=f"{file_path}/{name}",
                    config=config,
                    path=file_path,
                    block_type=BlockType.VARIABLE,
                    attributes=attributes,
                    id=f"{ArmElements.VARIABLES}.{name}",
                )
            )

    def _create_parameter_vertices(self, file_path: str, parameters: dict[str, dict[str, Any]] | None) -> None:
        if not parameters:
            return

        for name, config in parameters.items():
            if name in (START_LINE, END_LINE):
                continue
            if not isinstance(config, dict):
                logging.warning(f"[ArmLocalGraph] parameter {name} has wrong type {type(config)}")
                continue

            attributes = pickle_deepcopy(config)

            self.vertices.append(
                ArmBlock(
                    name=f"{file_path}/{name}",
                    config=config,
                    path=file_path,
                    block_type=BlockType.PARAMETER,
                    attributes=attributes,
                    id=f"{ArmElements.PARAMETERS}.{name}",
                )
            )

    def _create_resource_vertices(self, file_path: str, resources: list[dict[str, Any]] | None) -> None:
        if not resources:
            return

        for config in resources:
            if "type" not in config:
                # this can't be a real ARM resource without a "type" field
                return

            resource_name = config.get("name") or "unknown"
            resource_type = config["type"]

            attributes = pickle_deepcopy(config)
            attributes[CustomAttributes.RESOURCE_TYPE] = resource_type

            self.vertices.append(
                ArmBlock(
                    name=resource_name,
                    config=config,
                    path=file_path,
                    block_type=BlockType.RESOURCE,
                    attributes=attributes,
                    id=f"{resource_type}.{resource_name}"
                )
            )

    def _create_edges(self) -> None:
        for origin_vertex_index, vertex in enumerate(self.vertices):
            if DEPENDS_ON_FIELD in vertex.attributes:
                self._create_explicit_edge(origin_vertex_index, vertex.name, vertex.attributes['dependsOn'])
            self._create_implicit_edges(origin_vertex_index, vertex.name, vertex.attributes)

    def _create_explicit_edge(self, origin_vertex_index: int, resource_name: str, deps: list[str]) -> None:
        for dep in deps:
            if RESOURCE_ID_FUNC in dep:
                processed_dep = extract_resource_name_from_resource_id_func(dep)
            else:
                processed_dep = dep.split('/')[-1]
            # Check if the processed dependency exists in the map
            if processed_dep in self.vertices_by_name:
                self._create_edge(processed_dep, origin_vertex_index, f'{resource_name}->{processed_dep}')
            else:
                # Dependency not found
                logging.warning(f"[ArmLocalGraph] resource dependency {processed_dep} defined in {dep} for resource"
                                f" {resource_name} not found")
                continue

    def _create_vars_and_parameters_edges(self) -> None:
        pattern = r"(variables|parameters)\('(\w+)'\)"
        for origin_vertex_index, vertex in enumerate(self.vertices):
            for attr_key, attr_value in vertex.attributes.items():
                if not isinstance(attr_value, str):
                    continue
                if ArmElements.VARIABLES in attr_value or ArmElements.PARAMETERS in attr_value:
                    matches = re.findall(pattern, attr_value)
                    for match in matches:
                        var_name = match[1]
                        self._create_edge(f"{vertex.path}/{var_name}", origin_vertex_index, attr_key)

    def _create_edge(self, element_name: str, origin_vertex_index: int, label: str) -> None:
        dest_vertex_index = self.vertices_by_name.get(element_name)
        if origin_vertex_index == dest_vertex_index or dest_vertex_index is None:
            return
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)

    def _create_implicit_edges(self, origin_vertex_index: int, resource_name: str, resource: dict[str, Any]) -> None:
        for value in resource.values():
            if isinstance(value, str):
                if REFERENCE_FUNC in value:
                    self._create_implicit_edge(origin_vertex_index, resource_name, value)

    def _create_implicit_edge(self, origin_vertex_index: int, resource_name: str, reference_string: str) -> None:
        dep_name = extract_resource_name_from_reference_func(reference_string)
        self._create_edge(dep_name, origin_vertex_index, f'{resource_name}->{dep_name}')

    def _update_resource_vertices_names(self) -> None:
        for i, vertex in enumerate(self.vertices):
            if ((vertex.block_type != BlockType.RESOURCE or 'name' not in vertex.config or vertex.name == vertex.config['name'])
                    or not isinstance(vertex.config['name'], str)):
                continue

            if PARAMETER_FUNC in vertex.name or VARIABLE_FUNC in vertex.name:
                if vertex.name in self.vertices_by_name:
                    del self.vertices_by_name[vertex.name]

                vertex.name = vertex.config['name']
                self.vertices_by_name[vertex.name] = i

    def update_vertices_configs(self) -> None:
        for vertex in self.vertices:
            changed_attributes = list(vertex.changed_attributes.keys())
            changed_attributes = filter_sub_keys(changed_attributes)
            self.update_vertex_config(vertex, changed_attributes)

    @staticmethod
    def update_vertex_config(vertex: Block, changed_attributes: list[str] | dict[str, Any],
                             dynamic_blocks: bool = False) -> None:
        if not changed_attributes:
            # skip, if there is no change
            return

        for attr in changed_attributes:
            new_value = vertex.attributes.get(attr, None)
            if vertex.block_type == BlockType.RESOURCE:
                ArmLocalGraph.update_config_attribute(
                    config=vertex.config, key_to_update=attr, new_value=new_value
                )

    @staticmethod
    def update_config_attribute(config: list[Any] | dict[str, Any], key_to_update: str, new_value: Any) -> None:
        key_parts = key_to_update.split(".")

        if isinstance(config, dict):
            key = key_parts[0]
            if len(key_parts) == 1:
                ArmLocalGraph.update_config_value(config=config, key=key, new_value=new_value)
                return
            else:
                key, key_parts = ArmLocalGraph.adjust_key(config, key, key_parts)
                if len(key_parts) == 1:
                    ArmLocalGraph.update_config_value(config=config, key=key, new_value=new_value)
                    return

                ArmLocalGraph.update_config_attribute(config[key], ".".join(key_parts[1:]), new_value)
        elif isinstance(config, list):
            key_idx = force_int(key_parts[0])
            if key_idx is None:
                return

            if len(key_parts) == 1:
                ArmLocalGraph.update_config_value(config=config, key=key_idx, new_value=new_value)
                return
            else:
                ArmLocalGraph.update_config_attribute(config[key_idx], ".".join(key_parts[1:]), new_value)

        return

    @staticmethod
    def update_config_value(config: list[Any] | dict[str, Any], key: int | str, new_value: Any) -> None:
        new_value = adjust_value(config[key], new_value)  # type:ignore[index]
        if new_value is None:
            # couldn't find key in in value object
            return

        config[key] = new_value  # type:ignore[index]

    @staticmethod
    def adjust_key(config: dict[str, Any], key: str, key_parts: list[str]) -> tuple[str, list[str]]:
        """Adjusts the key, if it consists of multiple dots

        Ex:
        config = {"'container.registry'": "acrName"}
        key = "'container"
        key_parts = ["'container", "registry'"]

        returns new_key = "'container.registry'"
                new_key_parts = ["'container.registry'"]
        """

        if key not in config:
            if len(key_parts) >= 2:
                new_key = ".".join(key_parts[:2])
                new_key_parts = [new_key] + key_parts[2:]

                return ArmLocalGraph.adjust_key(config, new_key, new_key_parts)

        return key, key_parts

    def get_resources_types_in_graph(self) -> list[str]:
        # not used
        return []
