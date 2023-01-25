from __future__ import annotations

import os
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Any, Mapping, Union

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image

if TYPE_CHECKING:
    import networkx
    import igraph
    from typing_extensions import TypeAlias

_ExtractImagesCallableAlias: TypeAlias = Callable[["dict[str, Any]"], "list[str]"]


class GraphImageReferencerProvider:
    __slots__ = ("graph_connector", "supported_resource_types", "graph_framework")

    # TODO add to graph_connector type fot igraph and implement the extract_nodes_igraph function
    def __init__(self, graph_connector: Union[igraph.Graph, networkx.DiGraph],
                 supported_resource_types: dict[str, _ExtractImagesCallableAlias] | Mapping[
                     str, _ExtractImagesCallableAlias]):
        self.graph_connector = graph_connector
        self.supported_resource_types = supported_resource_types
        self.graph_framework = os.environ.get('CHECKOV_GRAPH_FRAMEWORK', 'NETWORKX')

    @abstractmethod
    def extract_images_from_resources(self) -> list[Image]:
        pass

    def extract_nodes(self) -> networkx.Graph | igraph.Graph:
        if self.graph_framework == 'NETWORKX':
            return self.extract_nodes_networkx()
        else:
            return self.extract_nodes_igraph()

    def extract_nodes_networkx(self) -> networkx.Graph:
        resource_nodes = [
            node
            for node, resource_type in self.graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
            if resource_type and resource_type in self.supported_resource_types
        ]

        return self.graph_connector.subgraph(resource_nodes)

    def extract_nodes_igraph(self) -> igraph.Graph:
        pass
