from __future__ import annotations

import logging
import re
from inspect import ismethod
from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING, Callable, cast

from checkov.cloudformation.graph_builder.graph_components.block_types import BlockType
from checkov.cloudformation.graph_builder.graph_components.blocks import CloudformationBlock
from checkov.cloudformation.graph_builder.utils import GLOBALS_RESOURCE_TYPE_MAP
from checkov.cloudformation.graph_builder.variable_rendering.renderer import CloudformationVariableRenderer
from checkov.cloudformation.parser.cfn_keywords import IntrinsicFunctions, ConditionFunctions, ResourceAttributes, \
    TemplateSections
from checkov.common.graph.graph_builder.consts import GraphSource
from checkov.common.parsers.node import DictNode
from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.data_structures_utils import search_deep_keys
from checkov.cloudformation.graph_builder.graph_components.generic_resource_encryption import ENCRYPTION_BY_RESOURCE_TYPE

if TYPE_CHECKING:
    from checkov.common.graph.graph_builder.graph_components.blocks import Block

TOKENIZED_FIELD_PATTERN = re.compile(r'\${([a-zA-Z0-9.]*)}')


class CloudformationLocalGraph(LocalGraph[CloudformationBlock]):
    SUPPORTED_RESOURCE_ATTR_CONNECTION_KEYS = (ResourceAttributes.DEPENDS_ON, IntrinsicFunctions.CONDITION)
    SUPPORTED_FN_CONNECTION_KEYS = (IntrinsicFunctions.GET_ATT, ConditionFunctions.IF,
                                    IntrinsicFunctions.REF, IntrinsicFunctions.FIND_IN_MAP, IntrinsicFunctions.CONDITION)

    def __init__(self, cfn_definitions: dict[str, dict[str, Any]], source: str = GraphSource.CLOUDFORMATION) -> None:
        super().__init__()
        self.definitions = cfn_definitions
        self.source = source
        self.vertices: "list[CloudformationBlock]" = []
        self._vertices_indexes: "dict[str, dict[str, int]]" = {}
        self.transform_pre: "dict[str, Any]" = {}
        self._edges_set: "set[Edge]" = set()
        self._connection_key_func = {
            IntrinsicFunctions.GET_ATT: self._fetch_getatt_target_id,
            ConditionFunctions.IF: self._fetch_if_target_id,
            IntrinsicFunctions.REF: self._fetch_ref_target_id,
            IntrinsicFunctions.FIND_IN_MAP: self._fetch_findinmap_target_id,
            IntrinsicFunctions.CONDITION: self._fetch_connection_target_id
        }

    def build_graph(self, render_variables: bool) -> None:
        self._create_vertices()
        logging.info(f"[CloudformationLocalGraph] created {len(self.vertices)} vertices")
        self._add_sam_globals()
        self._create_edges()
        logging.info(f"[CloudformationLocalGraph] created {len(self.edges)} edges")
        if render_variables:
            logging.info(f"Rendering variables, graph has {len(self.vertices)} vertices and {len(self.edges)} edges")
            renderer = CloudformationVariableRenderer(self)
            renderer.render_variables_from_local_graph()
            self.update_vertices_breadcrumbs()
        self.calculate_encryption_attribute(ENCRYPTION_BY_RESOURCE_TYPE)

    def _create_vertices(self) -> None:
        for file_path, file_conf in self.definitions.items():
            self._create_section_vertices(
                file_path,
                file_conf,
                TemplateSections.RESOURCES,
                BlockType.RESOURCE,
                self.extract_resource_attributes,  # type:ignore[arg-type]
            )
            self._create_section_vertices(file_path, file_conf, TemplateSections.OUTPUTS, BlockType.OUTPUTS)
            self._create_section_vertices(file_path, file_conf, TemplateSections.MAPPINGS, BlockType.MAPPINGS)
            self._create_section_vertices(file_path, file_conf, TemplateSections.CONDITIONS,
                                          BlockType.CONDITIONS)
            self._create_section_vertices(file_path, file_conf, TemplateSections.PARAMETERS,
                                          BlockType.PARAMETERS)
            self._create_section_vertices(file_path, file_conf, TemplateSections.GLOBALS,
                                          BlockType.GLOBALS)

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)

    def extract_resource_attributes(self, resource: DictNode) -> DictNode:
        resource_type = resource.get("Type")
        attributes: "DictNode" = resource.get("Properties", {})
        if not isinstance(attributes, dict):
            attributes = DictNode({}, resource.start_mark, resource.end_mark)
        attributes["resource_type"] = resource_type
        attributes[START_LINE] = resource.get(START_LINE)
        attributes[END_LINE] = resource.get(END_LINE)
        attributes.start_mark = resource.start_mark
        attributes.end_mark = attributes.end_mark
        return attributes

    def _create_section_vertices(
        self,
        file_path: str,
        file_conf: dict[str, Any],
        section: TemplateSections,
        block_type: str,
        attributes_operator: Callable[[dict[str, Any]], dict[str, Any]] = lambda a: a,
    ) -> None:
        for name, obj in get_only_dict_items(file_conf.get(section.value, {})).items():
            is_resources_section = section == TemplateSections.RESOURCES
            attributes = attributes_operator(obj)
            block_name = name if not is_resources_section else f"{obj.get('Type', 'UnTyped')}.{name}"
            config = obj if not is_resources_section else cast("dict[str, Any]", obj.get("Properties"))
            metadata = obj.get("Metadata")
            id = f"{block_type}.{block_name}" if not is_resources_section else block_name
            self.vertices.append(CloudformationBlock(
                name=block_name,
                config=config,
                path=file_path,
                block_type=block_type,
                attributes=attributes,
                id=id,
                source=self.source,
                metadata=metadata
            ))

            if not self._vertices_indexes.get(file_path):
                self._vertices_indexes[file_path] = {}
            self._vertices_indexes[file_path][name] = len(self.vertices) - 1

    def _add_sam_globals(self) -> None:
        # behaviour regarding overrides
        # https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-template-anatomy-globals.html#sam-specification-template-anatomy-globals-overrideable
        for index in self.vertices_by_block_type.get(BlockType.GLOBALS, []):
            globals_vertex = self.vertices[index]
            related_vertices = [
                vertex
                for vertex in self.vertices
                if vertex.block_type == BlockType.RESOURCE
                and vertex.path == globals_vertex.path
                and vertex.attributes.get("resource_type") == GLOBALS_RESOURCE_TYPE_MAP.get(globals_vertex.name)
            ]

            for property, value in globals_vertex.attributes.items():
                if property.endswith((START_LINE, END_LINE)):
                    continue
                if property.startswith("Tags"):
                    # TODO: support Tags properly
                    continue

                for vertex in related_vertices:
                    if property not in vertex.attributes:
                        self.update_vertex_attribute(
                            vertex_index=self.vertices.index(vertex),
                            attribute_key=property,
                            attribute_value=value,
                            change_origin_id=index,
                            attribute_at_dest=property,
                            transform_step=True,
                        )
                    elif isinstance(value, list):
                        self.update_vertex_attribute(
                            vertex_index=self.vertices.index(vertex),
                            attribute_key=property,
                            attribute_value=[*vertex.attributes[property], *value],
                            change_origin_id=index,
                            attribute_at_dest=property,
                            transform_step=True,
                        )

    def update_vertices_breadcrumbs(self) -> None:
        """
        The function processes each vertex's breadcrumbs:
        1. Get more data to each vertex in breadcrumb (name, path, hash and type)
        """
        for vertex in self.vertices:
            for attribute_key, breadcrumbs_list in vertex.changed_attributes.items():
                hash_breadcrumbs = []
                for breadcrumb in breadcrumbs_list:
                    breadcrumb_data = self.vertices[breadcrumb.vertex_id].get_export_data()
                    breadcrumb_data['attribute_key'] = breadcrumb.attribute_key
                    hash_breadcrumbs.append(breadcrumb_data)
                vertex.breadcrumbs[attribute_key] = hash_breadcrumbs

    def _add_resource_attr_connections(self, attribute: str) -> None:
        if attribute not in self.SUPPORTED_RESOURCE_ATTR_CONNECTION_KEYS:
            return
        for origin_node_index, vertex in enumerate(self.vertices):
            if vertex.block_type == BlockType.RESOURCE:
                vertex_path = vertex.path
                vertex_name = vertex.name.split('.')[-1]
                target_ids = self.definitions.get(vertex_path, {}) \
                    .get(TemplateSections.RESOURCES.value, {}).get(vertex_name, {}).get(attribute, None)
                target_ids = [target_ids] if isinstance(target_ids, str) else target_ids
                if isinstance(target_ids, list):
                    for target_id in target_ids:
                        if isinstance(target_id, str):
                            dest_vertex_index = self._vertices_indexes.get(vertex_path, {}).get(target_id, None)
                            if dest_vertex_index is not None:
                                self._create_edge(origin_node_index, dest_vertex_index, label=attribute)
                        else:
                            logging.debug(
                                f"[CloudformationLocalGraph] didnt create edge for target_id {target_id}"
                                f"and vertex_path {vertex_path} as target_id is not a string"
                            )
                else:
                    logging.debug(
                        f"[CloudformationLocalGraph] didnt create edge for target_ids {target_ids}"
                        f"and vertex_path {vertex_path} as target_ids is not a list"
                    )

    def _extract_source_value_attrs(self, matching_path: list[Any]) -> tuple[str, Any, list[Any]]:
        """ matching_path for Resource = [template_section, source_id, 'Properties', ... , key, value]
         matching_path otherwise = # matching_path for Resource = [template_section, source_id, ... , key, value]
         key = a member of SUPPORTED_FN_CONNECTION_KEYS """
        template_section = matching_path[0]
        source_id = matching_path[1]
        value = matching_path[-1]
        attrs_starting_index = 3 if template_section == TemplateSections.RESOURCES else 2
        attributes = matching_path[attrs_starting_index:-2]
        return source_id, value, attributes

    def _add_fn_connections(self, key: str) -> None:
        if key not in self.SUPPORTED_FN_CONNECTION_KEYS:
            return
        extract_target_id_func = self._connection_key_func.get(key, None)
        if not ismethod(extract_target_id_func):
            return

        for file_path, cfndict in self.definitions.items():
            matching_paths = self.search_deep_keys(key, cfndict)
            for matching_path in matching_paths:
                source_id, value, attributes = self._extract_source_value_attrs(matching_path)
                target_id = extract_target_id_func(cfndict, value)
                if target_id:
                    origin_vertex_index, dest_vertex_index, label = self._extract_origin_dest_label(
                        file_path, source_id, target_id, attributes)
                    if origin_vertex_index is not None and dest_vertex_index is not None:
                        self._create_edge(origin_vertex_index, dest_vertex_index, label)

    def search_deep_keys(self, searchText: str, cfndict: dict[str, Any], includeGlobals: bool = True) -> list[list[Any]]:
        """
            Search for a key in all parts of the template.
            :return if searchText is "Ref", an array like ['Resources', 'myInstance', 'Properties', 'ImageId', 'Ref', 'Ec2ImageId']
        """
        logging.debug(f'Search for key {searchText} as far down as the template goes')

        results: "list[list[int | str]]" = []
        results.extend(search_deep_keys(searchText, cfndict, []))
        # Globals are removed during a transform.  They need to be checked manually
        if includeGlobals:
            cfn_globals: "dict[str, Any] | None" = self.transform_pre.get('Globals')
            pre_results = search_deep_keys(searchText, cfn_globals, [])
            for pre_result in pre_results:
                results.append(['Globals', *pre_result])
        return results

    def _fetch_if_target_id(self, cfndict: dict[str, Any], value: Any) -> Optional[int]:
        target_id = None
        # value = [condition_name, value_if_true, value_if_false]
        if isinstance(value, list) and len(value) == 3 and (self._is_of_type(cfndict, value[0], TemplateSections.CONDITIONS)):
            target_id = value[0]
        return target_id

    def _fetch_getatt_target_id(self, cfndict: dict[str, Any], value: Any) -> Optional[int]:
        """ might be one of the 2 following notations:
         1st: { "Fn::GetAtt" : [ "logicalNameOfResource", "attributeName" ] }
         2nd: { "!GetAtt" : "logicalNameOfResource.attributeName" } """
        target_id = None

        # Fn::GetAtt notation
        if isinstance(value, list) and len(value) == 2 and (self._is_of_type(cfndict, value[0], TemplateSections.RESOURCES)):
            target_id = value[0]

        # !GetAtt notation
        if isinstance(value, str) and '.' in value:
            resource_id = value.split('.')[0]
            if self._is_of_type(cfndict, resource_id, TemplateSections.RESOURCES):
                target_id = resource_id

        return target_id

    def _fetch_ref_target_id(self, cfndict: dict[str, Any], value: Any) -> int | str | None:
        target_id = None
        # value might be a string or a list of strings
        if isinstance(value, (str, int)) \
                and (self._is_of_type(cfndict, value, TemplateSections.RESOURCES, TemplateSections.PARAMETERS)):
            target_id = value
        return target_id

    def _fetch_connection_target_id(self, cfndict: dict[str, Any], value: Any) -> int | str | None:
        target_id = None
        # value might be a string or a list of strings
        if isinstance(value, (str, int)) \
                and (self._is_of_type(cfndict, value, TemplateSections.CONDITIONS)):
            target_id = value
        return target_id

    def _fetch_findinmap_target_id(self, cfndict: dict[str, Any], value: Any) -> Optional[int]:
        target_id = None
        # value = [ MapName, TopLevelKey, SecondLevelKey ]
        if isinstance(value, list) and len(value) == 3 and (self._is_of_type(cfndict, value[0], TemplateSections.MAPPINGS)):
            target_id = value[0]
        return target_id

    def _add_fn_sub_connections(self) -> None:
        for file_path, cfndict in self.definitions.items():
            # add edges for "Fn::Sub" tags. E.g. { "Fn::Sub": "arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:vpc/${vpc}" }
            sub_objs = self.search_deep_keys(IntrinsicFunctions.SUB, cfndict)
            for sub_obj in sub_objs:
                sub_parameters = []
                sub_parameter_values = {}
                source_id, value, attributes = self._extract_source_value_attrs(sub_obj)

                if isinstance(value, list):
                    if not value:
                        continue
                    if len(value) == 2:
                        sub_parameter_values = value[1]
                    sub_parameters = self._find_fn_sub_parameter(value[0])
                elif isinstance(value, str):
                    sub_parameters = self._find_fn_sub_parameter(value)

                for sub_parameter in sub_parameters:
                    if sub_parameter not in sub_parameter_values:
                        if '.' in sub_parameter:
                            sub_parameter = sub_parameter.split('.')[0]
                        origin_vertex_index, dest_vertex_index, label = self._extract_origin_dest_label(
                            file_path, source_id, sub_parameter, attributes)
                        if origin_vertex_index is not None and dest_vertex_index is not None:
                            self._create_edge(origin_vertex_index, dest_vertex_index, label)

    def _extract_origin_dest_label(
        self, file_path: str, source_id: str, target_id: str, attributes: list[Any]
    ) -> tuple[int | None, int | None, str]:
        origin_vertex_index = self._vertices_indexes.get(file_path, {}).get(source_id, None)
        dest_vertex_index = self._vertices_indexes.get(file_path, {}).get(target_id, None)
        attributes_joined = '.'.join(map(str, attributes))  # mapping all attributes to str because one of the attrs might be an int
        return origin_vertex_index, dest_vertex_index, attributes_joined

    @staticmethod
    def _find_fn_sub_parameter(string: str) -> list[str]:
        """Search string for tokenized fields"""
        try:
            return TOKENIZED_FIELD_PATTERN.findall(string)
        except Exception as e:
            logging.warning(f'cant find fn sub parameter for: {string}, error: {str(e)}')
            return []

    def _fill_in_out_edges(self) -> None:
        for i in range(len(self.vertices)):
            if i not in self.in_edges:
                self.in_edges[i] = []
            if i not in self.out_edges:
                self.out_edges[i] = []

    def get_resources_types_in_graph(self) -> List[str]:
        return []

    def _create_edges(self) -> None:
        self._add_resource_attr_connections(ResourceAttributes.DEPENDS_ON)
        self._add_resource_attr_connections(IntrinsicFunctions.CONDITION)
        self._add_fn_connections(IntrinsicFunctions.CONDITION)
        self._add_fn_connections(IntrinsicFunctions.GET_ATT)
        self._add_fn_connections(ConditionFunctions.IF)
        self._add_fn_connections(IntrinsicFunctions.REF)
        self._add_fn_connections(IntrinsicFunctions.FIND_IN_MAP)
        self._add_fn_sub_connections()
        self._fill_in_out_edges()

    def _create_edge(self, origin_vertex_index: int, dest_vertex_index: int, label: str) -> None:
        if origin_vertex_index == dest_vertex_index or not label:
            return
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        if edge not in self._edges_set:
            self._edges_set.add(edge)
            self.edges.append(edge)
            self.out_edges[origin_vertex_index].append(edge)
            self.in_edges[dest_vertex_index].append(edge)

    @staticmethod
    def _is_of_type(cfndict: dict[str, Any], identifier: Any, *template_sections: TemplateSections) -> bool:
        if isinstance(identifier, str):
            for ts in template_sections:
                ts_var = cfndict.get(ts, {})
                if ts_var is None:
                    continue
                if ts_var.get(identifier):
                    return True
        return False

    def update_vertices_configs(self) -> None:
        # not used
        pass

    @staticmethod
    def update_vertex_config(
        vertex: Block, changed_attributes: list[str] | dict[str, Any], dynamic_blocks: bool = False
    ) -> None:
        # not used
        pass


def get_only_dict_items(origin_dict: Union[Dict[str, Any], Any]) -> Dict[str, Dict[str, Any]]:
    if not isinstance(origin_dict, dict):
        return {}
    return {key: value for key, value in origin_dict.items() if isinstance(value, dict)}
