from __future__ import annotations

from typing import TYPE_CHECKING

from hcl2 import START_LINE, END_LINE

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.images.image_referencer import Image
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.common.util.type_forcers import force_list, extract_json

if TYPE_CHECKING:
    from networkx import DiGraph

SUPPORTED_AWS_IMAGE_RESOURCE_TYPES = {
    "aws_apprunner_service",
    "aws_batch_job_definition",
    "aws_codebuild_project",
    "aws_ecs_task_definition",
    "aws_lightsail_container_service_deployment_version",
}


def extract_images_from_aws_resources(graph_connector: DiGraph) -> list[Image]:
    images = []
    image_names = []

    resource_nodes = [
        node
        for node, resource_type in graph_connector.nodes(data=CustomAttributes.RESOURCE_TYPE)
        if resource_type and resource_type in SUPPORTED_AWS_IMAGE_RESOURCE_TYPES
    ]

    supported_resources_graph = graph_connector.subgraph(resource_nodes)

    for _, resource in supported_resources_graph.nodes(data=True):
        if resource[CustomAttributes.RESOURCE_TYPE] == "aws_apprunner_service":
            image_repo = find_in_dict(input_dict=resource, key_path="source_configuration/image_repository")
            if isinstance(image_repo, dict):
                repo_type = image_repo.get("image_repository_type")
                name = image_repo.get("image_identifier")
                if name and isinstance(name, str) and repo_type == "ECR_PUBLIC":
                    image_names.append(name)

        elif resource[CustomAttributes.RESOURCE_TYPE] == "aws_batch_job_definition":
            properties = extract_json(resource.get("container_properties"))
            if isinstance(properties, dict):
                name = properties.get("image")
                if name and isinstance(name, str):
                    image_names.append(name)
                node_range = find_in_dict(
                    input_dict=properties,
                    key_path="nodeProperties/nodeRangeProperties"
                )
                if isinstance(node_range, list):
                    for node in node_range:
                        name = find_in_dict(input_dict=node, key_path="container/image")
                        if name and isinstance(name, str):
                            image_names.append(name)

        elif resource[CustomAttributes.RESOURCE_TYPE] == "aws_codebuild_project":
            name = find_in_dict(input_dict=resource, key_path="environment/image")
            if name and isinstance(name, str) and not name.startswith("aws/codebuild/"):  # AWS provided images have an internal identifier
                image_names.append(name)

        elif resource[CustomAttributes.RESOURCE_TYPE] == "aws_ecs_task_definition":
            definitions = extract_json(resource.get("container_definitions"))
            if isinstance(definitions, list):
                for definition in definitions:
                    name = definition.get("image")
                    if name and isinstance(name, str):
                        image_names.append(name)

        elif resource[CustomAttributes.RESOURCE_TYPE] == "aws_lightsail_container_service_deployment_version":
            containers = resource.get("container")
            if containers:
                for container in force_list(containers):
                    name = container.get("image")
                    if name and isinstance(name, str):
                        image_names.append(name)

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
