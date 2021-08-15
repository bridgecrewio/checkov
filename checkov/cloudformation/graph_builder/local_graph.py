import logging
from typing import Dict, Any

import dpath.util
import six
from cfnlint.template import Template

from checkov.cloudformation.graph_builder.graph_components.block_types import CloudformationTemplateSections, BlockType
from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock
from checkov.cloudformation.parser.cfn_keywords import IntrinsicFunctions, ConditionFunctions, ResourceAttributes
from checkov.cloudformation.parser.node import dict_node
from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.local_graph import LocalGraph


class CloudformationLocalGraph(LocalGraph):
    SUPPORTED_RESOURCE_ATTR_CONNECTION_KEYS = (ResourceAttributes.DEPENDS_ON.value, IntrinsicFunctions.CONDITION.value)
    SUPPORTED_FN_CONNECTION_KEYS = (IntrinsicFunctions.GET_ATT.value, ConditionFunctions.IF.value,
                                    IntrinsicFunctions.REF.value, IntrinsicFunctions.FIND_IN_MAP.value)

    def __init__(self, cfn_definitions: Dict[str, dict_node], source: str = "CloudFormation") -> None:
        super().__init__()
        self.definitions = cfn_definitions
        self.source = source
        self._vertices_indexes = {}
        self._templates = {}
        self._edges_set = set()
        self._templates = {file_path: Template(file_path, definition)
                           for file_path, definition in self.definitions.items()}
        self._connection_key_func = {
            IntrinsicFunctions.GET_ATT.value: self._fetch_getatt_target_id,
            ConditionFunctions.IF.value: self._fetch_if_target_id,
            IntrinsicFunctions.REF.value: self._fetch_ref_target_id,
            IntrinsicFunctions.FIND_IN_MAP.value: self._fetch_findinmap_target_id
        }

    def build_graph(self, render_variables: bool) -> None:
        self._create_vertices()
        logging.info(f"[CloudformationLocalGraph] created {len(self.vertices)} vertices")
        self._create_edges()
        logging.info(f"[CloudformationLocalGraph] created {len(self.edges)} edges")

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

            if not self._vertices_indexes.get(file_path):
                self._vertices_indexes[file_path] = {}
            self._vertices_indexes[file_path][name] = len(self.vertices) - 1

    def _add_resource_attr_connections(self, attribute):
        if attribute not in self.SUPPORTED_RESOURCE_ATTR_CONNECTION_KEYS:
            return
        for origin_node_index, vertex in enumerate(self.vertices):
            if vertex.block_type == BlockType.RESOURCE:
                vertex_path = vertex.path
                vertex_name = vertex.name.split('.')[-1]
                vertex_definition = dpath.get(self.definitions,
                                              [vertex_path, CloudformationTemplateSections.RESOURCES.value,
                                               vertex_name])
                target_ids = vertex_definition.get(attribute)
                if isinstance(target_ids, (list, six.string_types)):
                    if isinstance(target_ids, (six.string_types)):
                        target_ids = [target_ids]
                    for target_id in target_ids:
                        if isinstance(target_id, six.string_types):
                            dest_vertex_index = self._vertices_indexes[vertex_path][target_id]
                            self._create_edge(origin_node_index, dest_vertex_index, label=attribute)

    def _add_fn_connections(self, key) -> None:
        if key not in self.SUPPORTED_FN_CONNECTION_KEYS:
            return
        for file_path, template in self._templates.items():
            matching_paths = template.search_deep_keys(key)
            for matching_path in matching_paths:
                # matching_path = [ref_type, source_id, 'Properties', ... , key, value]
                # value might be a string or a list of strings
                source_id = matching_path[1]
                value = matching_path[-1]
                attributes = matching_path[3:-2]

                fetch_target_id_func = self._connection_key_func.get(key, None)
                if fetch_target_id_func:
                    target_id = fetch_target_id_func(template, source_id, value)
                    if target_id:
                        origin_node_index = self._vertices_indexes[file_path][source_id]
                        dest_vertex_index = self._vertices_indexes[file_path][target_id]
                        attributes_joined = '.'.join(map(str, attributes))  # mapping all attributes to str because one of the attrs might be an int
                        self._create_edge(origin_node_index, dest_vertex_index, label=attributes_joined)

    def _fetch_if_target_id(self, template, source_id, value) -> int:
        target_id = None
        # value = [condition_name, value_if_true, value_if_false]
        if isinstance(value, list) and len(value) == 3 and (self._is_condition(template, value[0])):
            target_id = value[0]
        return target_id

    def _fetch_getatt_target_id(self, template, source_id, value) -> int:
        """ might be one of the 2 following notations:
         1st: { "Fn::GetAtt" : [ "logicalNameOfResource", "attributeName" ] }
         2nd: { "!GetAtt" : "logicalNameOfResource.attributeName" } """
        target_id = None

        # Fn::GetAtt notation
        if isinstance(value, list) and len(value) == 2 and (self._is_resource(template, value[0])):
            target_id = value[0]

        # !GetAtt notation
        if isinstance(value, (six.string_types, six.text_type)) and '.' in value:
            if self._is_resource(template, value.split('.')[0]):
                target_id = value.split('.')[0]

        return target_id

    def _fetch_ref_target_id(self, template, source_id, value) -> int:
        target_id = None
        # value might be a string or a list of strings
        if isinstance(value, (six.text_type, six.string_types, int)) \
                and (self._is_resource(template, source_id)) \
                and ((self._is_resource(template, value)) or (self._is_parameter(template, value))):
            target_id = value
        return target_id

    def _fetch_findinmap_target_id(self, template, source_id, value) -> int:
        target_id = None
        # value = [ MapName, TopLevelKey, SecondLevelKey ]
        if isinstance(value, list) and len(value) == 3 and (self._is_mapping(template, value[0])):
            target_id = value[0]
        return target_id

    def _create_edges(self) -> None:
        self._add_resource_attr_connections(ResourceAttributes.DEPENDS_ON.value)
        self._add_resource_attr_connections(IntrinsicFunctions.CONDITION.value)
        self._add_fn_connections(IntrinsicFunctions.GET_ATT.value)
        self._add_fn_connections(ConditionFunctions.IF.value)
        self._add_fn_connections(IntrinsicFunctions.REF.value)
        self._add_fn_connections(IntrinsicFunctions.FIND_IN_MAP.value)

    def _create_edge(self, origin_vertex_index: int, dest_vertex_index: int, label: str) -> None:
        if origin_vertex_index == dest_vertex_index:
            return
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        if edge not in self._edges_set:
            self._edges_set.add(edge)
            self.edges.append(edge)
            self.out_edges[origin_vertex_index].append(edge)
            self.in_edges[dest_vertex_index].append(edge)

    @staticmethod
    def _is_parameter(template, identifier):
        """Check if the identifier is that of a Parameter"""
        return template.template.get(CloudformationTemplateSections.PARAMETERS, {}).get(identifier, {})

    @staticmethod
    def _is_mapping(template, identifier):
        """Check if the identifier is that of a Mapping"""
        return template.template.get(CloudformationTemplateSections.MAPPINGS, {}).get(identifier, {})

    @staticmethod
    def _is_condition(template, identifier):
        """Check if the identifier is that of a Condition"""
        return template.template.get(CloudformationTemplateSections.CONDITIONS, {}).get(identifier, {})

    @staticmethod
    def _is_resource(template, identifier):
        """Check if the identifier is that of a Resource"""
        return template.template.get(CloudformationTemplateSections.RESOURCES, {}).get(identifier, {})


def get_only_dict_items(origin_dict: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {key: value for key, value in origin_dict.items() if isinstance(value, dict)}
