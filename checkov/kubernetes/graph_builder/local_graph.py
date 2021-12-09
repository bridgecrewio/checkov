import logging
from copy import deepcopy
from typing import List, Dict

from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock
from checkov.kubernetes.kubernetes_utils import is_invalid_k8_definition, get_resource_id


class KubernetesLocalGraph(LocalGraph):
    def __init__(self, definitions: Dict[str, List]):
        self.definitions = definitions
        super().__init__()

    def build_graph(self, render_variables: bool):
        self._create_vertices()

    def _create_vertices(self):
        for file_path, file_conf in self.definitions.items():
            for resource in file_conf:
                if resource.get('kind') == "List":
                    file_conf.extend(resource.get("items", []))
                    file_conf.remove(resource)

            for resource in file_conf:
                resource_type = resource.get('kind')
                metadata = resource.get('metadata') or {}
                # TODO: add support for generateName
                name = metadata.get('name')
                if is_invalid_k8_definition(resource) or metadata.get("ownerReferences") or not name:
                    logging.info(f"failed to create a vertex in file {file_path}")
                    file_conf.remove(resource)
                    continue

                config = deepcopy(resource)
                attributes = deepcopy(config)
                attributes["resource_type"] = resource_type
                attributes["__startline__"] = resource["__startline__"]
                attributes["__endline__"] = resource["__endline__"]
                block_id = get_resource_id(resource)

                self.vertices.append(KubernetesBlock(
                    block_name=block_id,
                    resource_type=resource_type,
                    config=config,
                    path=file_path,
                    attributes=attributes
                ))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
