from __future__ import annotations

from typing import Any

from checkov.common.typing import LibraryGraph
from checkov.common.util.data_structures_utils import find_in_dict
from checkov.common.util.type_forcers import force_list, extract_json
from checkov.terraform.image_referencer.base_provider import BaseTerraformProvider


class AwsTerraformProvider(BaseTerraformProvider):
    def __init__(self, graph_connector: LibraryGraph) -> None:
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_AWS_IMAGE_RESOURCE_TYPES,
        )


def extract_images_from_aws_apprunner_service(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    image_repo = find_in_dict(input_dict=resource, key_path="source_configuration/image_repository")
    if isinstance(image_repo, dict):
        repo_type = image_repo.get("image_repository_type")
        name = image_repo.get("image_identifier")
        if name and isinstance(name, str) and repo_type == "ECR_PUBLIC":
            image_names.append(name)

    return image_names


def extract_images_from_aws_batch_job_definition(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    properties = extract_json(resource.get("container_properties"))
    if isinstance(properties, dict):
        name = properties.get("image")
        if name and isinstance(name, str):
            image_names.append(name)

    # node properties are not supported yet
    # https://github.com/hashicorp/terraform-provider-aws/issues/20983

    return image_names


def extract_images_from_aws_codebuild_project(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    name = find_in_dict(input_dict=resource, key_path="environment/image")
    if name and isinstance(name, str):
        # AWS provided images have an internal identifier
        if not name.startswith("aws/codebuild/"):
            image_names.append(name)

    return image_names


def extract_images_from_aws_ecs_task_definition(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    definitions = extract_json(resource.get("container_definitions"))
    if isinstance(definitions, list):
        for definition in definitions:
            if isinstance(definition, dict):
                name = definition.get("image")
                if name and isinstance(name, str):
                    image_names.append(name)

    return image_names


def extract_images_from_aws_lightsail_container_service_deployment_version(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    containers = resource.get("container")
    if containers:
        for container in force_list(containers):
            if isinstance(container, dict):
                name = container.get("image")
                if name and isinstance(name, str):
                    image_names.append(name)

    return image_names


def extract_images_from_aws_sagemaker_image_version(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    image_name = find_in_dict(input_dict=resource, key_path="base_image")
    if image_name and isinstance(image_name, str):
        image_names.append(image_name)

    return image_names


def extract_images_from_aws_sagemaker_model(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    containers = resource.get("container")
    if containers:
        for container in force_list(containers):
            if isinstance(container, dict):
                name = container.get("image")
                if name and isinstance(name, str):
                    image_names.append(name)

    containers = resource.get("primary_container")
    if containers:
        for container in force_list(containers):
            if isinstance(container, dict):
                name = container.get("image")
                if name and isinstance(name, str):
                    image_names.append(name)

    return image_names


# needs to be at the bottom to add the defined functions
SUPPORTED_AWS_IMAGE_RESOURCE_TYPES = {
    "aws_apprunner_service": extract_images_from_aws_apprunner_service,
    "aws_batch_job_definition": extract_images_from_aws_batch_job_definition,
    "aws_codebuild_project": extract_images_from_aws_codebuild_project,
    "aws_ecs_task_definition": extract_images_from_aws_ecs_task_definition,
    "aws_lightsail_container_service_deployment_version": extract_images_from_aws_lightsail_container_service_deployment_version,
    "aws_sagemaker_image_version": extract_images_from_aws_sagemaker_image_version,
    "aws_sagemaker_model": extract_images_from_aws_sagemaker_model,
}
