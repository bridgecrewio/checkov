from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Union

import igraph

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image
    from networkx import DiGraph


class GraphImageReferencerManager:
    __slots__ = ("graph_connector",)

    def __init__(self, graph_connector: Union[igraph.Graph, DiGraph]) -> None:
        self.graph_connector = graph_connector

    @abstractmethod
    def extract_images_from_resources(self) -> list[Image]:
        pass
