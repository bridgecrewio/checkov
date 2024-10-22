from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.cloudformation.image_referencer.base_provider import BaseCloudFormationProvider
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.common.util.type_forcers import extract_json

if TYPE_CHECKING:
    from networkx import DiGraph


class AwsCloudFormationProvider(BaseCloudFormationProvider):
    def __init__(self, graph_connector: DiGraph) -> None:
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_AWS_IMAGE_RESOURCE_TYPES,
        )


def extract_images_from_aws_apprunner_service(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    image_repo = find_in_dict(input_dict=resource, key_path="SourceConfiguration/ImageRepository")
    if isinstance(image_repo, dict):
        repo_type = image_repo.get("ImageRepositoryType")
        name = image_repo.get("ImageIdentifier")
        if name and isinstance(name, str) and repo_type == "ECR_PUBLIC":
            image_names.append(name)

    return image_names


def extract_images_from_aws_batch_job_definition(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    properties = extract_json(resource.get("ContainerProperties"))
    if isinstance(properties, dict):
        name = properties.get("Image")
        if name and isinstance(name, str):
            image_names.append(name)

    node_range = find_in_dict(input_dict=resource, key_path="NodeProperties/NodeRangeProperties")
    if isinstance(node_range, list):
        for node in node_range:
            name = find_in_dict(input_dict=node, key_path="Container/Image")
            if name and isinstance(name, str):
                image_names.append(name)

    return image_names


def extract_images_from_aws_codebuild_project(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    name = find_in_dict(input_dict=resource, key_path="Environment/Image")
    if name and isinstance(name, str):
        # AWS provided images have an internal identifier
        if not name.startswith("aws/codebuild/"):
            image_names.append(name)

    return image_names


def extract_images_from_aws_ecs_task_definition(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    definitions = extract_json(resource.get("ContainerDefinitions"))
    if isinstance(definitions, list):
        for definition in definitions:
            name = definition.get("Image")
            if name and isinstance(name, str):
                image_names.append(name)

    return image_names


def extract_images_from_aws_lightsail_container_service_deployment_version(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    containers = find_in_dict(input_dict=resource, key_path="ContainerServiceDeployment/Containers")
    if isinstance(containers, list):
        for container in containers:
            name = container.get("Image")
            if name and isinstance(name, str):
                image_names.append(name)

    return image_names


def extract_images_from_aws_sagemaker_image_version(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    image_name = find_in_dict(input_dict=resource, key_path="BaseImage")
    if image_name and isinstance(image_name, str):
        image_names.append(image_name)

    return image_names


def extract_images_from_aws_sagemaker_model(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    image_name = find_in_dict(input_dict=resource, key_path="PrimaryContainer/Image")
    if image_name and isinstance(image_name, str):
        image_names.append(image_name)

    containers = find_in_dict(input_dict=resource, key_path="Containers")
    if isinstance(containers, list):
        for container in containers:
            name = container.get("Image")
            if name and isinstance(name, str):
                image_names.append(name)

    return image_names


# needs to be at the bottom to add the defined functions
SUPPORTED_AWS_IMAGE_RESOURCE_TYPES = {
    "AWS::AppRunner::Service": extract_images_from_aws_apprunner_service,
    "AWS::Batch::JobDefinition": extract_images_from_aws_batch_job_definition,
    "AWS::CodeBuild::Project": extract_images_from_aws_codebuild_project,
    "AWS::ECS::TaskDefinition": extract_images_from_aws_ecs_task_definition,
    "AWS::Lightsail::Container": extract_images_from_aws_lightsail_container_service_deployment_version,
    "AWS::SageMaker::ImageVersion": extract_images_from_aws_sagemaker_image_version,
    "AWS::SageMaker::Model": extract_images_from_aws_sagemaker_model,
}
