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

        def extract_resource_attributes(resource: dict_node) -> dict_node:
            resource_type = resource.get("Type")
            attributes = resource.get("Properties", {})
            attributes["resource_type"] = resource_type
            attributes["__startline__"] = resource["__startline__"]
            attributes["__endline__"] = resource["__endline__"]
            attributes.start_mark = resource.start_mark
            attributes.end_mark = attributes.end_mark
            return attributes

        for file_path, file_conf in self.definitions.items():
            self._create_section_vertices(file_path, file_conf, CloudformationTemplateSections.RESOURCES,
                                          BlockType.RESOURCE, extract_resource_attributes)
            self._create_section_vertices(file_path, file_conf, CloudformationTemplateSections.OUTPUTS, BlockType.OUTPUT)
            self._create_section_vertices(file_path, file_conf, CloudformationTemplateSections.MAPPINGS, BlockType.MAPPING)
            self._create_section_vertices(file_path, file_conf, CloudformationTemplateSections.CONDITIONS,
                                          BlockType.CONDITION)
            self._create_section_vertices(file_path, file_conf, CloudformationTemplateSections.PARAMETERS,
                                          BlockType.PARAMETER)

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)


    def _create_section_vertices(self, file_path: str, file_conf: dict, section: CloudformationTemplateSections,
                                 block_type: str, attributes_operator: callable = lambda a: a) -> None:
        for name, obj in get_only_dict_items(file_conf.get(section.value, {})).items():
            is_resources_section = section == CloudformationTemplateSections.RESOURCES
            attributes = attributes_operator(obj)
            block_name = name if not is_resources_section else f"{obj.get('Type', 'UnTyped')}.{name}"
            config = obj if not is_resources_section else obj.get("Properties")
            id = f"{block_type}.{block_name}" if not is_resources_section else block_name
            self.vertices.append(CloudformationBlock(
                name=block_name,
                config=config,
                path=file_path,
                block_type=block_type,
                attributes=attributes,
                id=id,
                source=self.source
            ))

def get_only_dict_items(origin_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {key: value for key, value in origin_dict.items() if isinstance(value, dict)}
