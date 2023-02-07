from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any, List, Dict
from collections import defaultdict

from checkov.common.graph.graph_builder import Edge
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock, KubernetesBlockMetadata, KubernetesSelector
from checkov.kubernetes.kubernetes_utils import DEFAULT_NESTED_RESOURCE_TYPE, is_invalid_k8_definition, get_resource_id, is_invalid_k8_pod_definition, \
    remove_metadata_from_attribute, PARENT_RESOURCE_KEY_NAME, PARENT_RESOURCE_ID_KEY_NAME, SUPPORTED_POD_CONTAINERS_TYPES
from checkov.kubernetes.kubernetes_graph_flags import K8sGraphFlags
from checkov.kubernetes.graph_builder.graph_components.edge_builders.LabelSelectorEdgeBuilder import LabelSelectorEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.edge_builders.KeywordEdgeBuilder import KeywordEdgeBuilder
from checkov.kubernetes.graph_builder.graph_components.edge_builders.NetworkPolicyEdgeBuilder import NetworkPolicyEdgeBuilder


class KubernetesLocalGraph(LocalGraph[KubernetesBlock]):
    def __init__(self, definitions: dict[str, list[dict[str, Any]]]) -> None:
        self.definitions = definitions
        self.edge_builders = (LabelSelectorEdgeBuilder, KeywordEdgeBuilder, NetworkPolicyEdgeBuilder)
        super().__init__()

    def build_graph(self, render_variables: bool, graph_flags: K8sGraphFlags | None = None) -> None:
        if graph_flags is None:
            graph_flags = K8sGraphFlags()

        self._create_vertices(create_complex_vertices=graph_flags.create_complex_vertices)
        if graph_flags.create_edges:
            self._create_edges()

    def _create_vertices(self, create_complex_vertices: bool) -> None:
        for file_path, file_conf in self.definitions.items():

            if create_complex_vertices:
                file_conf = self._extract_nested_resources(file_conf)

            for resource in file_conf:
                resource_type = resource.get('kind', DEFAULT_NESTED_RESOURCE_TYPE)
                metadata = resource.get('metadata') or {}
                # TODO: add support for generateName

                if resource_type == DEFAULT_NESTED_RESOURCE_TYPE:
                    if is_invalid_k8_pod_definition(resource):
                        logging.info(f"failed to create a vertex in file {file_path}")
                        file_conf.remove(resource)
                        continue

                else:
                    if is_invalid_k8_definition(resource) or not metadata.get('name'):
                        logging.info(f"failed to create a vertex in file {file_path}")
                        file_conf.remove(resource)
                        continue

                config = deepcopy(resource)
                attributes = deepcopy(config)
                attributes["resource_type"] = resource_type
                attributes["kind"] = resource_type
                attributes[START_LINE] = resource[START_LINE]
                attributes[END_LINE] = resource[END_LINE]

                block_id = get_resource_id(resource)
                if not block_id:
                    continue

                block_metadata = None
                if create_complex_vertices:
                    block_metadata = KubernetesLocalGraph._get_k8s_block_metadata(resource)

                self.vertices.append(KubernetesBlock(
                    block_name=block_id,
                    resource_type=resource_type,
                    config=config,
                    path=file_path,
                    attributes=attributes,
                    metadata=block_metadata
                ))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)

    def _create_edges(self) -> None:
        edges_to_create = defaultdict(list)
        for vertex_index, vertex in enumerate(self.vertices):
            for edge_builder in self.edge_builders:
                if edge_builder.should_search_for_edges(vertex):
                    current_vertex_connections = edge_builder.find_connections(vertex, self.vertices)
                    if current_vertex_connections:
                        edges_to_create[vertex.name].extend(current_vertex_connections)
            for destination_vertex_index in edges_to_create[vertex.name]:
                self._create_edge(vertex_index, destination_vertex_index, vertex.name)

    def _create_edge(self, origin_vertex_index: int, dest_vertex_index: int, label: str) -> None:
        edge = Edge(origin_vertex_index, dest_vertex_index, label)
        self.edges.append(edge)
        self.out_edges[origin_vertex_index].append(edge)
        self.in_edges[dest_vertex_index].append(edge)

    @staticmethod
    def _get_k8s_block_metadata(resource: Dict[str, Any]) -> KubernetesBlockMetadata:
        name = resource.get('metadata', {}).get('name')
        spec = resource.get('spec')
        match_labels: Dict[str, Any] | None = None
        if isinstance(spec, list):
            for spec_item in spec:
                if spec_item.get('selector'):
                    if resource.get('kind') == "Service":
                        match_labels = spec_item.get('selector')
                    else:
                        match_labels = spec_item.get('selector').get('matchLabels')
                    break
            else:
                match_labels = None
        elif isinstance(spec, dict):
            if spec.get('selector'):
                if isinstance(spec.get('selector'), dict):
                    if resource.get('kind') == "Service":
                        match_labels = spec.get('selector')
                    else:
                        match_labels = spec.get('selector', {}).get('matchLabels')
        remove_metadata_from_attribute(match_labels)
        selector = KubernetesSelector(match_labels)
        labels = resource.get('metadata', {}).get('labels')
        remove_metadata_from_attribute(labels)
        return KubernetesBlockMetadata(selector, labels, name)

    @staticmethod
    def _extract_nested_resources(file_conf: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_resources: "list[dict[str, Any]]" = []
        for conf in file_conf:
            KubernetesLocalGraph._extract_nested_resources_recursive(conf, all_resources)
        return all_resources

    @staticmethod
    def _extract_nested_resources_recursive(conf: Dict[str, Any], all_resources: List[Dict[str, Any]]) -> None:
        spec = conf.get('spec')
        if not spec or not isinstance(spec, dict):
            all_resources.append(conf)
            return
        template = spec.get('template', None)
        if not template or not isinstance(template, dict):
            all_resources.append(conf)
            return
        if is_invalid_k8_pod_definition(template):
            all_resources.append(conf)
            return
        if conf.get('kind') in SUPPORTED_POD_CONTAINERS_TYPES:
            # means this is a Pod resource nested in a supported template container resource
            template[PARENT_RESOURCE_ID_KEY_NAME] = get_resource_id(conf)
            metadata = conf.get('metadata', {})
            if not metadata:
                # resource does not contain all required fields and can not be associated with the pod
                all_resources.append(conf)
                return
            template[PARENT_RESOURCE_KEY_NAME] = metadata.get('name', "")
            spec.pop('template', None)
        else:
            template = {}
        all_resources.append(conf)
        KubernetesLocalGraph._extract_nested_resources_recursive(template, all_resources)

    def update_vertices_configs(self) -> None:
        # not used
        return None

    @staticmethod
    def update_vertex_config(vertex: KubernetesBlock, changed_attributes: list[str] | dict[str, Any], dynamic_blocks: bool = False) -> None:
        # not used
        return None

    def get_resources_types_in_graph(self) -> list[str]:
        # not used
        return []
