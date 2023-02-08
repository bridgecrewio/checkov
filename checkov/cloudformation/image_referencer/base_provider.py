from __future__ import annotations

import os

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.graph.image_referencer_provider import GraphImageReferencerProvider
from checkov.common.images.image_referencer import Image
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.str_utils import removeprefix


class BaseCloudFormationProvider(GraphImageReferencerProvider):

    def extract_images_from_resources(self) -> list[Image]:
        images = []

        supported_resources_graph = self.extract_nodes()

        for resource in self.extract_resource(supported_resources_graph):
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
                        related_resource_id=f'{removeprefix(resource.get("file_path_", ""), os.getenv("BC_ROOT_DIR", ""))}:{resource.get("id_")}',
                    )
                )

        return images
