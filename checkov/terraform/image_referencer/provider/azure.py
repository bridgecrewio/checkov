from __future__ import annotations

from typing import Any

from checkov.common.typing import LibraryGraph
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.common.util.type_forcers import force_list
from checkov.terraform.image_referencer.base_provider import BaseTerraformProvider


class AzureTerraformProvider(BaseTerraformProvider):
    def __init__(self, graph_connector: LibraryGraph) -> None:
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_AZURE_IMAGE_RESOURCE_TYPES,
        )


def extract_images_from_azurerm_batch_pool(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    containers = find_in_dict(input_dict=resource, key_path="container_configuration/container_image_names")
    if isinstance(containers, list):
        image_names.extend(container for container in containers if isinstance(container, str))

    return image_names


def extract_images_from_azurerm_container_group(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    containers = resource.get("container")
    if containers:
        for container in force_list(containers):
            name = container.get("image")
            if name and isinstance(name, str):
                image_names.append(name)
    containers = resource.get("init_container")
    if containers:
        for container in force_list(containers):
            name = container.get("image")
            if name and isinstance(name, str):
                image_names.append(name)

    return image_names


def extract_images_from_azurerm_linux_function_app(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    docker = find_in_dict(input_dict=resource, key_path="site_config/application_stack/docker")
    if isinstance(docker, dict):
        name = docker.get("image_name")
        tag = docker.get("image_tag")
        if name and isinstance(name, str) and tag and isinstance(tag, str):
            image_names.append(f"{name}:{tag}")

    return image_names


def extract_images_from_azurerm_linux_web_app(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    app_stack = find_in_dict(input_dict=resource, key_path="site_config/application_stack")
    if isinstance(app_stack, dict):
        name = app_stack.get("docker_image")
        tag = app_stack.get("docker_image_tag")
        if name and isinstance(name, str) and tag and isinstance(tag, str):
            image_names.append(f"{name}:{tag}")

    return image_names


def extract_images_from_azurerm_spring_cloud_container_deployment(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    name = resource.get("image")
    if name and isinstance(name, str):
        image_names.append(name)

    return image_names


def extract_images_from_azurerm_windows_web_app(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    app_stack = find_in_dict(input_dict=resource, key_path="site_config/application_stack")
    if isinstance(app_stack, dict):
        name = app_stack.get("docker_container_name")
        tag = app_stack.get("docker_container_tag")
        if name and isinstance(name, str) and tag and isinstance(tag, str):
            image_names.append(f"{name}:{tag}")

    return image_names


# needs to be at the bottom to add the defined functions
SUPPORTED_AZURE_IMAGE_RESOURCE_TYPES = {
    "azurerm_batch_pool": extract_images_from_azurerm_batch_pool,
    "azurerm_container_group": extract_images_from_azurerm_container_group,
    "azurerm_linux_function_app": extract_images_from_azurerm_linux_function_app,
    "azurerm_linux_function_app_slot": extract_images_from_azurerm_linux_function_app,
    "azurerm_linux_web_app": extract_images_from_azurerm_linux_web_app,
    "azurerm_linux_web_app_slot": extract_images_from_azurerm_linux_web_app,
    "azurerm_spring_cloud_container_deployment": extract_images_from_azurerm_spring_cloud_container_deployment,
    "azurerm_windows_web_app": extract_images_from_azurerm_windows_web_app,
    "azurerm_windows_web_app_slot": extract_images_from_azurerm_windows_web_app,
}
