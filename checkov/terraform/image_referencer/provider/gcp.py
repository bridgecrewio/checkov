from __future__ import annotations

from typing import Any

from checkov.common.typing import LibraryGraph
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.terraform.image_referencer.base_provider import BaseTerraformProvider


class GcpTerraformProvider(BaseTerraformProvider):
    def __init__(self, graph_connector: LibraryGraph) -> None:
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_GCP_IMAGE_RESOURCE_TYPES,
        )


def extract_images_from_google_cloudbuild_trigger(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    steps = find_in_dict(input_dict=resource, key_path="build/step")
    if isinstance(steps, list):
        for definition in steps:
            name = definition.get("name")
            if name and isinstance(name, str):
                image_names.append(name)

    return image_names


def extract_images_from_google_cloud_run_service(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    name = find_in_dict(input_dict=resource, key_path="template/spec/containers/image")
    if name and isinstance(name, str):
        image_names.append(name)

    return image_names


def extract_images_from_google_cloud_run_v2_job(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    name = find_in_dict(input_dict=resource, key_path="template/template/containers/image")
    if name and isinstance(name, str):
        image_names.append(name)

    return image_names


def extract_images_from_google_cloud_run_v2_service(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    name = find_in_dict(input_dict=resource, key_path="template/containers/image")
    if name and isinstance(name, str):
        image_names.append(name)

    return image_names


# needs to be at the bottom to add the defined functions
SUPPORTED_GCP_IMAGE_RESOURCE_TYPES = {
    "google_cloudbuild_trigger": extract_images_from_google_cloudbuild_trigger,
    "google_cloud_run_service": extract_images_from_google_cloud_run_service,
    "google_cloud_run_v2_job": extract_images_from_google_cloud_run_v2_job,
    "google_cloud_run_v2_service": extract_images_from_google_cloud_run_v2_service,
}
