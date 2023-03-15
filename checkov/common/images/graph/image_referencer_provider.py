from __future__ import annotations

import itertools
import os
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Any, Mapping, Union, Generator

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image

if TYPE_CHECKING:
    import networkx
    import igraph
    from typing_extensions import TypeAlias

_ExtractImagesCallableAlias: TypeAlias = Callable[["dict[str, Any]"], "list[str]"]


class GraphImageReferencerProvider:
    __slots__ = ("graph_connector", "supported_resource_types", "graph_framework")

    def __init__(self, graph_connector: Union[igraph.Graph, networkx.DiGraph],
                 supported_resource_types: dict[str, _ExtractImagesCallableAlias] | Mapping[
                     str, _ExtractImagesCallableAlias]):
        self.graph_connector = graph_connector
        self.supported_resource_types = supported_resource_types
        self.graph_framework = os.environ.get('CHECKOV_GRAPH_FRAMEWORK', 'NETWORKX')

    @abstractmethod
    def extract_images_from_resources(self) -> list[Image]:
        pass

    def extract_nodes(self) -> networkx.Graph | igraph.Graph | None:
        if self.graph_framework == 'IGRAPH':
            return self.extract_nodes_igraph()
        else:  # the default value of the graph framework is 'NETWORKX'
            return self.extract_nodes_networkx()

    def extract_nodes_networkx(self) -> networkx.Graph:
        resource_nodes = [
            node
            for node, resource_type in self.graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
            if resource_type and resource_type in self.supported_resource_types
        ]

        return self.graph_connector.subgraph(resource_nodes)

    def extract_nodes_igraph(self) -> igraph.Graph:
        resource_nodes = [
            node
            for node, resource_type in itertools.zip_longest(self.graph_connector.vs['name'],
                                                             self.graph_connector.vs[CustomAttributes.RESOURCE_TYPE])
            if resource_type and resource_type in self.supported_resource_types
        ]
        return self.graph_connector.subgraph(resource_nodes)

    def extract_resource(self, supported_resources_graph: networkx.Graph | igraph.Graph) -> \
            Generator[dict[str, Any], dict[str, Any], dict[str, Any]]:
        def extract_resource_networkx(graph: networkx.Graph) -> Generator[dict[str, Any], None, None]:
            for _, resource in graph.nodes(data=True):
                yield resource

        def extract_resource_igraph(graph: igraph.Graph) -> Generator[dict[str, Any], None, None]:
            for v in graph.vs:
                resource = {
                    'name': v['name'],
                    'block_type_': v[CustomAttributes.BLOCK_TYPE],
                    'resource_type': v[CustomAttributes.RESOURCE_TYPE]
                }
                resource.update(v['attr'])
                yield resource

        graph_resource = None
        if self.graph_framework == 'NETWORKX':
            graph_resource = extract_resource_networkx(supported_resources_graph)
        elif self.graph_framework == 'IGRAPH':
            graph_resource = extract_resource_igraph(supported_resources_graph)

        return graph_resource  # type: ignore
