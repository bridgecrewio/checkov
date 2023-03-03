from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.common.images.graph.image_referencer_manager import GraphImageReferencerManager
from checkov.kubernetes.image_referencer.provider.k8s import KubernetesProvider

if TYPE_CHECKING:
    from checkov.common.images.image_referencer import Image


class KubernetesImageReferencerManager(GraphImageReferencerManager):

    def extract_images_from_resources(self) -> list[Image]:
        k8s_provider = KubernetesProvider(graph_connector=self.graph_connector)

        images = k8s_provider.extract_images_from_resources()

        return images
