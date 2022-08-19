from __future__ import annotations

from typing import TYPE_CHECKING

from hcl2 import START_LINE, END_LINE

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.common.util.type_forcers import force_list

if TYPE_CHECKING:
    from networkx import DiGraph

SUPPORTED_AWS_IMAGE_RESOURCE_TYPES = {
    "azurerm_batch_pool",
    "azurerm_container_group",
    "azurerm_linux_function_app",
    "azurerm_linux_function_app_slot",
    "azurerm_linux_web_app",
    "azurerm_linux_web_app_slot",
    "azurerm_spring_cloud_container_deployment",
    "azurerm_windows_web_app",
    "azurerm_windows_web_app_slot",
}


def extract_images_from_azure_resources(graph_connector: DiGraph) -> list[Image]:
    images = []

    resource_nodes = [
        node
        for node, resource_type in graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
        if resource_type and resource_type in SUPPORTED_AWS_IMAGE_RESOURCE_TYPES
    ]

    supported_resources_graph = graph_connector.subgraph(resource_nodes)

    for _, resource in supported_resources_graph.nodes(data=True):
        image_names: list[str] = []
        resource_type = resource[CustomAttributes.RESOURCE_TYPE]

        if resource_type == "azurerm_batch_pool":
            containers = find_in_dict(input_dict=resource, key_path="container_configuration/container_image_names")
            if isinstance(containers, list):
                image_names.extend(container for container in containers if isinstance(container, str))

        elif resource_type == "azurerm_container_group":
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

        elif resource_type in ("azurerm_linux_function_app", "azurerm_linux_function_app_slot"):
            docker = find_in_dict(input_dict=resource, key_path="site_config/application_stack/docker")
            if isinstance(docker, dict):
                name = docker.get("image_name")
                tag = docker.get("image_tag")
                if name and isinstance(name, str) and tag and isinstance(tag, str):
                    image_names.append(f"{name}:{tag}")

        elif resource_type in ("azurerm_linux_web_app", "azurerm_linux_web_app_slot"):
            app_stack = find_in_dict(input_dict=resource, key_path="site_config/application_stack")
            if isinstance(app_stack, dict):
                name = app_stack.get("docker_image")
                tag = app_stack.get("docker_image_tag")
                if name and isinstance(name, str) and tag and isinstance(tag, str):
                    image_names.append(f"{name}:{tag}")

        elif resource_type == "azurerm_spring_cloud_container_deployment":
            name = resource.get("image")
            if name and isinstance(name, str):
                image_names.append(name)

        elif resource_type in ("azurerm_windows_web_app", "azurerm_windows_web_app_slot"):
            app_stack = find_in_dict(input_dict=resource, key_path="site_config/application_stack")
            if isinstance(app_stack, dict):
                name = app_stack.get("docker_container_name")
                tag = app_stack.get("docker_container_tag")
                if name and isinstance(name, str) and tag and isinstance(tag, str):
                    image_names.append(f"{name}:{tag}")

        for name in image_names:
            images.append(
                Image(
                    file_path=resource[CustomAttributes.FILE_PATH],
                    name=name,
                    start_line=resource[START_LINE],
                    end_line=resource[END_LINE],
                )
            )

    return images