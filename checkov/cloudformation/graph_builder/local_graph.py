import logging
from typing import Dict

from checkov.cloudformation.graph_builder.graph_components.block_types import CloudformationTemplateSections, BlockType
from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock
from checkov.common.graph.graph_builder.local_graph import LocalGraph


class CloudformationLocalGraph(LocalGraph):
    def __init__(self, cfn_definitions: Dict, source="CloudFormation") -> None:
        super(CloudformationLocalGraph, self).__init__()
        self.definitions = cfn_definitions
        self.source = source

    def build_graph(self, render_variables: bool) -> None:
        self._create_vertices()
        logging.info(f"[CloudformationLocalGraph] created {len(self.vertices)} vertices")

    def _create_vertices(self) -> None:
        for file_path, file_conf in self.definitions.items():
            self._create_resources_vertices(file_path, get_only_dict_items(file_conf.get(CloudformationTemplateSections.RESOURCES.value, [])))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)

    def _create_resources_vertices(self, file_path, resources):
        for resource_name, resource in resources.items():
            resource = resources[resource_name]
            resource_type = resource.get("Type")
            attributes = resource.get("Properties", {})
            attributes["resource_type"] = resource_type
            attributes["__startline__"] = resource["__startline__"]
            attributes["__endline__"] = resource["__endline__"]
            attributes.start_mark = resource.start_mark
            attributes.end_mark = attributes.end_mark
            block = CloudformationBlock(name=".".join([resource_type, resource_name]),
                                        config=resource.get("Properties"),
                                        path=file_path,
                                        block_type=BlockType.RESOURCE,
                                        attributes=attributes,
                                        id=".".join([resource_type, resource_name]),
                                        source=self.source
                                        )
            self.vertices.append(block)


def get_only_dict_items(origin_dict: Dict) -> Dict:
    return {key: origin_dict[key] for key in origin_dict.keys() if isinstance(origin_dict[key], dict)}
