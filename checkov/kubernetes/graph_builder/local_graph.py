import logging
from copy import deepcopy
from typing import Any, List, Dict

from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock, KubernetesBlockMetadata, KubernetesSelector
from checkov.kubernetes.kubernetes_utils import DEFAULT_NESTED_RESOURCE_TYPE, is_invalid_k8_definition, get_resource_id, is_invalid_k8_pod_definition


class KubernetesLocalGraph(LocalGraph):
    def __init__(self, definitions: Dict[str, List]):
        self.definitions = definitions
        super().__init__()

    def build_graph(self, render_variables: bool, create_complex_vertices: bool = False):
        self._create_vertices(create_complex_vertices)

    def _create_vertices(self, create_complex_vertices: bool):
        for file_path, file_conf in self.definitions.items():
            for resource in file_conf:
                if resource.get('kind') == "List":
                    file_conf.extend(item for item in resource.get("items", []) if item)
                    file_conf.remove(resource)

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
                attributes["__startline__"] = resource["__startline__"]
                attributes["__endline__"] = resource["__endline__"]
                block_id = get_resource_id(resource)
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

    @staticmethod
    def _get_k8s_block_metadata(resource: Dict[str, Any]) -> KubernetesBlockMetadata:
        name = resource.get('metadata', {}).get('name')
        spec = resource.get('spec')
        if isinstance(spec, list):
            for spec_item in spec:
                if spec_item.get('selector'):
                    match_labels = spec_item.get('selector').get('matchLabels')
                    break
            else:
                match_labels = None
        elif isinstance(spec, dict):
            match_labels = spec.get('selector', {}).get('matchLabels')
        else:
            match_labels = None
        selector = KubernetesSelector(match_labels)
        labels = resource.get('metadata', {}).get('labels')
        return KubernetesBlockMetadata(selector, labels, name)

    @staticmethod
    def _extract_nested_resources(file_conf: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_resources = []
        for conf in file_conf:
            KubernetesLocalGraph._extract_nested_resources_recursive(conf, all_resources)
        return all_resources
            
    @staticmethod
    def _extract_nested_resources_recursive(conf: Dict[str, Any], all_resources: List[Dict[str, Any]]):
        spec = conf.get('spec')
        if not spec or not isinstance(spec, dict):
            all_resources.append(conf)
            return
        template = spec.get('template', None)
        if not template or not isinstance(template, dict):
            all_resources.append(conf)
            return
        spec.pop('template', None)
        all_resources.append(conf)
        KubernetesLocalGraph._extract_nested_resources_recursive(template, all_resources)
