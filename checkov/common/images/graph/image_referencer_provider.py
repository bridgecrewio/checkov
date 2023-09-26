from __future__ import annotations

import itertools
import os
import typing
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Any, Mapping, Generator

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.common.typing import LibraryGraph

if TYPE_CHECKING:
    import networkx
    import igraph
    import rustworkx
    from typing_extensions import TypeAlias

_ExtractImagesCallableAlias: TypeAlias = Callable[["dict[str, Any]"], "list[str]"]


class GraphImageReferencerProvider:
    __slots__ = ("graph_connector", "supported_resource_types", "graph_framework")

    def __init__(self, graph_connector: LibraryGraph,
                 supported_resource_types: dict[str, _ExtractImagesCallableAlias] | Mapping[
                     str, _ExtractImagesCallableAlias]):
        self.graph_connector = graph_connector
        self.supported_resource_types = supported_resource_types
        self.graph_framework = os.environ.get('CHECKOV_GRAPH_FRAMEWORK', 'IGRAPH')

    @abstractmethod
    def extract_images_from_resources(self) -> list[Image]:
        pass

    def extract_nodes(self) -> LibraryGraph | None:
        if self.graph_framework == 'IGRAPH':
            return self.extract_nodes_igraph()
        elif self.graph_framework == 'RUSTWORKX':
            return self.extract_nodes_rustworkx()
        else:
            return self.extract_nodes_networkx()

    def extract_nodes_networkx(self) -> networkx.Graph:
        if typing.TYPE_CHECKING:
            self.graph_connector = typing.cast(networkx.Graph, self.graph_connector)
        resource_nodes = [
            node
            for node, resource_type in self.graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
            if resource_type and resource_type in self.supported_resource_types
        ]

        return self.graph_connector.subgraph(resource_nodes)

    def extract_nodes_rustworkx(self) -> rustworkx.PyDiGraph[Any, Any]:
        resource_nodes = [
            index
            for index, node in self.graph_connector.nodes()
            if self.resource_type_pred(node, list(self.supported_resource_types))
        ]

        return self.graph_connector.subgraph(resource_nodes)

    def extract_nodes_igraph(self) -> igraph.Graph:
        if typing.TYPE_CHECKING:
            self.graph_connector = typing.cast(igraph.Graph, self.graph_connector)
        resource_nodes = [
            node
            for node, resource_type in itertools.zip_longest(self.graph_connector.vs['name'],
                                                             self.graph_connector.vs[CustomAttributes.RESOURCE_TYPE])
            if resource_type and resource_type in self.supported_resource_types
        ]
        return self.graph_connector.subgraph(resource_nodes)

    def extract_resource(self, supported_resources_graph: LibraryGraph) -> \
            Generator[dict[str, Any], dict[str, Any], dict[str, Any]]:
        def extract_resource_networkx(graph: networkx.Graph) -> Generator[dict[str, Any], None, None]:
            for _, resource in graph.nodes(data=True):
                yield resource

        def extract_resource_rustworkx(graph: rustworkx.PyDiGraph[Any, Any]) -> Generator[dict[str, Any], None, None]:
            for _, resource in graph.nodes():
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
        elif self.graph_framework == 'RUSTWORKX':
            graph_resource = extract_resource_rustworkx(supported_resources_graph)

        return graph_resource  # type: ignore

    @staticmethod
    def resource_type_pred(v: dict[str, Any], resource_types: list[str]) -> bool:
        return not resource_types or ("resource_type" in v and v["resource_type"] in resource_types)
