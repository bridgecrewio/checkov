import logging
from typing import Dict, Any

from checkov.cloudformation.graph_builder.graph_components.block_types import CloudformationTemplateSections, BlockType
from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock
from checkov.cloudformation.parser.node import dict_node
from checkov.common.graph.graph_builder.local_graph import LocalGraph


class CloudformationLocalGraph(LocalGraph):
    def __init__(self, cfn_definitions: Dict[str, dict_node], source: str = "CloudFormation") -> None:
        super().__init__()
        self.definitions = cfn_definitions
        self.source = source

    def build_graph(self, render_variables: bool) -> None:
        self._create_vertices()
        logging.info(f"[CloudformationLocalGraph] created {len(self.vertices)} vertices")

    def _create_vertices(self) -> None:
        for file_path, file_conf in self.definitions.items():
            self._create_resources_vertices(
                file_path, get_only_dict_items(file_conf.get(CloudformationTemplateSections.RESOURCES.value, {}))
            )

            self._create_parameters_vertices(
                file_path, get_only_dict_items(file_conf.get(CloudformationTemplateSections.PARAMETERS.value, {}))
            )

            self._create_outputs_vertices(
                file_path, get_only_dict_items(file_conf.get(CloudformationTemplateSections.OUTPUTS.value, {}))
            )

            self._create_conditions_vertices(
                file_path, get_only_dict_items(file_conf.get(CloudformationTemplateSections.CONDITIONS.value, {}))
            )

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)

    def _create_resources_vertices(self, file_path: str, resources: Dict[str, dict_node]) -> None:
        for resource_name, resource in resources.items():
            resource_type = resource.get("Type")
            attributes = resource.get("Properties", {})
            attributes["resource_type"] = resource_type
            attributes["__startline__"] = resource["__startline__"]
            attributes["__endline__"] = resource["__endline__"]
            attributes.start_mark = resource.start_mark
            attributes.end_mark = attributes.end_mark
            block = CloudformationBlock(
                name=f"{resource_type}.{resource_name}",
                config=resource.get("Properties", {}),
                path=file_path,
                block_type=BlockType.RESOURCE,
                attributes=attributes,
                id=f"{resource_type}.{resource_name}",
                source=self.source,
            )
            self.vertices.append(block)

    def _create_parameters_vertices(self, file_path: str, params: Dict[str, dict_node]):
        for param_name, parameter in params.items():
            self.vertices.append(CloudformationBlock(
                name=param_name,
                path=file_path,
                config=parameter,
                block_type=BlockType.PARAMETER,
                id=f"{BlockType.PARAMETER}.{param_name}",
                source=self.source,
                attributes=parameter
            ))

    def _create_outputs_vertices(self, file_path: str, outputs: Dict[str, dict_node]):
        for output_name, output in outputs.items():
            self.vertices.append(CloudformationBlock(
                name=output_name,
                path=file_path,
                config=output,
                block_type=BlockType.OUTPUT,
                id=f"{BlockType.OUTPUT}.{output_name}",
                source=self.source,
                attributes=output
            ))

    def _create_conditions_vertices(self, file_path: str, conditions: Dict[str, dict_node]):
        for cond_name, cond in conditions.items():
            self.vertices.append(CloudformationBlock(
                name=cond_name,
                path=file_path,
                config=cond,
                block_type=BlockType.CONDITION,
                id=f"{BlockType.CONDITION}.{cond_name}",
                source=self.source,
                attributes=cond
            ))


def get_only_dict_items(origin_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {key: value for key, value in origin_dict.items() if isinstance(value, dict)}
