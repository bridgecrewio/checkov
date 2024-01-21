from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.images.graph.image_referencer_manager import GraphImageReferencerManager
from checkov.common.typing import LibraryGraph
from checkov.helm.image_referencer.provider.helm import HelmProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image


class HelmImageReferencerManager(GraphImageReferencerManager):

    def __init__(self, graph_connector: LibraryGraph, original_root_dir: str, temp_root_dir: str):
        super().__init__(graph_connector)
        self.original_root_dir = original_root_dir
        self.temp_root_dir = temp_root_dir

    def extract_images_from_resources(self) -> list[Image]:
        helm_provider = HelmProvider(graph_connector=self.graph_connector, original_root_dir=self.original_root_dir,
                                     temp_root_dir=self.temp_root_dir)
        images = helm_provider.extract_images_from_resources()

        return images
