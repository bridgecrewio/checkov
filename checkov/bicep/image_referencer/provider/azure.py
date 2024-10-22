from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.bicep.image_referencer.base_provider import BaseBicepProvider
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.common.util.type_forcers import force_list

if TYPE_CHECKING:
    from networkx import DiGraph


class AzureBicepProvider(BaseBicepProvider):
    def __init__(self, graph_connector: DiGraph) -> None:
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_AZURE_IMAGE_RESOURCE_TYPES,
        )


def extract_images_from_azurerm_batch_pool(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    containers = find_in_dict(
        input_dict=resource,
        key_path="properties/virtualMachineConfiguration/containerConfiguration/containerImageNames",
    )
    if isinstance(containers, list):
        image_names.extend(container for container in containers if isinstance(container, str))

    return image_names


def extract_images_from_azurerm_container_group(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    properties = resource.get("properties")
    if properties and isinstance(properties, dict):
        containers = properties.get("containers")
        if containers:
            for container in force_list(containers):
                name = find_in_dict(input_dict=container, key_path="properties/image")
                if name and isinstance(name, str):
                    image_names.append(name)
        containers = properties.get("initContainers")
        if containers:
            for container in force_list(containers):
                name = find_in_dict(input_dict=container, key_path="properties/image")
                if name and isinstance(name, str):
                    image_names.append(name)

    return image_names


def extract_images_from_azurerm_web_app(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    containers = find_in_dict(input_dict=resource, key_path="properties/template/containers")
    if containers:
        for container in force_list(containers):
            name = container.get("image")
            if name and isinstance(name, str):
                image_names.append(name)

    return image_names


# needs to be at the bottom to add the defined functions
SUPPORTED_AZURE_IMAGE_RESOURCE_TYPES = {
    "Microsoft.App/containerApps": extract_images_from_azurerm_web_app,
    "Microsoft.Batch/batchAccounts/pools": extract_images_from_azurerm_batch_pool,
    "Microsoft.ContainerInstance/containerGroups": extract_images_from_azurerm_container_group,
    "Microsoft.Web/containerApps": extract_images_from_azurerm_web_app,
}
