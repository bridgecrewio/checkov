from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image

if TYPE_CHECKING:
    from networkx import DiGraph, Graph
    from typing_extensions import TypeAlias

_ExtractImagesCallableAlias: TypeAlias = Callable[["dict[str, Any]"], "list[str]"]


class GraphImageReferencerProvider:
    __slots__ = ("graph_connector", "supported_resource_types")

    def __init__(self, graph_connector: DiGraph, supported_resource_types: dict[str, _ExtractImagesCallableAlias]):
        self.graph_connector = graph_connector
        self.supported_resource_types = supported_resource_types

    @abstractmethod
    def extract_images_from_resources(self) -> list[Image]:
        pass

    def extract_nodes_networkx(self) -> Graph:
        resource_nodes = [
            node
            for node, resource_type in self.graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
            if resource_type and resource_type in self.supported_resource_types
        ]

        return self.graph_connector.subgraph(resource_nodes)

    def extract_nodes_igraph(self):  # type: ignore
        pass
