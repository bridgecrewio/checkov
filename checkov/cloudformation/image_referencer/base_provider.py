from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, Any

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.str_utils import removeprefix

if TYPE_CHECKING:
    from networkx import DiGraph
    from typing_extensions import TypeAlias

_ExtractImagesCallableAlias: TypeAlias = Callable[["dict[str, Any]"], "list[str]"]


class BaseCloudFormationProvider:
    __slots__ = ("graph_connector", "supported_resource_types")

    def __init__(
        self, graph_connector: DiGraph, supported_resource_types: dict[str, _ExtractImagesCallableAlias]
    ) -> None:
        self.graph_connector = graph_connector
        self.supported_resource_types = supported_resource_types

    def extract_images_from_resources(self) -> list[Image]:
        images = []

        resource_nodes = [
            node
            for node, resource_type in self.graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
            if resource_type and resource_type in self.supported_resource_types
        ]

        supported_resources_graph = self.graph_connector.subgraph(resource_nodes)

        for _, resource in supported_resources_graph.nodes(data=True):
            image_names: list[str] = []
            resource_type = resource[CustomAttributes.RESOURCE_TYPE]

            extract_images_func = self.supported_resource_types.get(resource_type)
            if extract_images_func:
                image_names.extend(extract_images_func(resource))

            for name in image_names:
                images.append(
                    Image(
                        file_path=resource[CustomAttributes.FILE_PATH],
                        name=name,
                        start_line=resource[START_LINE],
                        end_line=resource[END_LINE],
                        related_resource_id=f'{removeprefix(resource.get("file_path_"), os.getenv("BC_ROOT_DIR", ""))}:{resource.get("id_")}',
                    )
                )

        return images
