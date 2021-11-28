from typing import List, Union, Dict, Any

from checkov.common.graph.graph_builder.graph_components.blocks import Block
from checkov.common.graph.graph_builder.local_graph import LocalGraph
from checkov.common.parsers.node import DictNode
from checkov.kubernetes.graph_builder.graph_components.blocks import KubernetesBlock


class KubernetesLocalGraph(LocalGraph):
    def __init__(self, definitions: Dict[str, DictNode]):
        self.definitions = definitions
        super().__init__()

    def build_graph(self, render_variables: bool):
        self._create_vertices()

    def _create_vertices(self):
        for file_path, file_conf in self.definitions.items():
            for resource in file_conf:
                resource_type = resource.get('kind')
                name = resource.get('metadata', {}).get('name')
                if not resource_type or not name:
                    continue

                namespace = resource.get('metadata', {}).get('namespace', 'default')
                config = resource.get('spec', {})

                attributes = config.copy()
                attributes["resource_type"] = resource_type
                attributes["__startline__"] = resource["__startline__"]
                attributes["__endline__"] = resource["__endline__"]

                self.vertices.append(KubernetesBlock(
                    name=name,
                    namespace=namespace,
                    resource_type=resource_type,
                    config=config,
                    path=file_path,
                    attributes=attributes
                ))

        for i, vertex in enumerate(self.vertices):
            self.vertices_by_block_type[vertex.block_type].append(i)
            self.vertices_block_name_map[vertex.block_type][vertex.name].append(i)
