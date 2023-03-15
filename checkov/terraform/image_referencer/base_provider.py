from __future__ import annotations

import os

from hcl2 import START_LINE as HCL_START_LINE, END_LINE as HCL_END_LINE

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.graph.image_referencer_provider import GraphImageReferencerProvider
from checkov.common.images.image_referencer import Image
from checkov.common.util.consts import START_LINE, END_LINE
from checkov.common.util.str_utils import removeprefix
from checkov.terraform.graph_builder.utils import setup_file_path_to_referred_id, get_related_resource_id


class BaseTerraformProvider(GraphImageReferencerProvider):

    def extract_images_from_resources(self) -> list[Image]:
        images = []
        supported_resources_graph = self.extract_nodes()
        file_path_to_referred_id = setup_file_path_to_referred_id(self.graph_connector)

        for resource in self.extract_resource(supported_resources_graph):
            image_names: list[str] = []
            resource_type = resource[CustomAttributes.RESOURCE_TYPE]

            extract_images_func = self.supported_resource_types.get(resource_type)
            if extract_images_func:
                image_names.extend(extract_images_func(resource))

            if not image_names:
                # no need to process any further
                continue

            start_line = 0
            end_line = 0
            if all(key in resource for key in (HCL_START_LINE, HCL_END_LINE)):
                # hcl file
                start_line = resource[HCL_START_LINE]
                end_line = resource[HCL_END_LINE]
            elif all(key in resource for key in (START_LINE, END_LINE)):
                # TF plan file
                start_line = resource[START_LINE]
                end_line = resource[END_LINE]

            related_resource_id = get_related_resource_id(resource, file_path_to_referred_id)
            for name in image_names:
                images.append(
                    Image(
                        file_path=resource[CustomAttributes.FILE_PATH],
                        name=name,
                        start_line=start_line,
                        end_line=end_line,
                        related_resource_id=f'{removeprefix(resource.get("file_path_", ""), os.getenv("BC_ROOT_DIR", ""))}:{related_resource_id}'
                    )
                )

        return images
