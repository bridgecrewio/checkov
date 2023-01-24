from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.common.util.data_structures_utils import find_in_dict
from checkov.kubernetes.image_referencer.base_provider import BaseKubernetesProvider

if TYPE_CHECKING:
    from networkx import DiGraph
    from checkov.common.images.graph.image_referencer_provider import _ExtractImagesCallableAlias


class KubernetesProvider(BaseKubernetesProvider):
    def __init__(self, graph_connector: DiGraph) -> None:
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_K8S_IMAGE_RESOURCE_TYPES,
        )


def extract_images_from_cron_job(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    spec = find_in_dict(input_dict=resource, key_path="spec/jobTemplate/spec/template/spec")
    if isinstance(spec, dict):
        containers = spec.get("containers")
        image_names.extend(extract_images_from_containers(containers=containers))

        containers = spec.get("initContainers")
        image_names.extend(extract_images_from_containers(containers=containers))

    return image_names


def extract_images_from_pod(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    spec = resource.get("spec")
    if isinstance(spec, dict):
        containers = spec.get("containers")
        image_names.extend(extract_images_from_containers(containers=containers))

        containers = spec.get("initContainers")
        image_names.extend(extract_images_from_containers(containers=containers))

    return image_names


def extract_images_from_pod_template(resource: dict[str, Any]) -> list[str]:
    # the 'PodTemplate' object is usually not defined by the user, but rather used by Kubernetes internally
    image_names: list[str] = []

    spec = find_in_dict(input_dict=resource, key_path="template/spec")
    if isinstance(spec, dict):
        containers = spec.get("containers")
        image_names.extend(extract_images_from_containers(containers=containers))

        containers = spec.get("initContainers")
        image_names.extend(extract_images_from_containers(containers=containers))

    return image_names


def extract_images_from_template(resource: dict[str, Any]) -> list[str]:
    image_names: list[str] = []

    spec = find_in_dict(input_dict=resource, key_path="spec/template/spec")
    if isinstance(spec, dict):
        containers = spec.get("containers")
        image_names.extend(extract_images_from_containers(containers=containers))

        containers = spec.get("initContainers")
        image_names.extend(extract_images_from_containers(containers=containers))

    return image_names


def extract_images_from_containers(containers: Any) -> list[str]:
    """Helper function to extract image names from containers block"""

    image_names: list[str] = []

    if isinstance(containers, list):
        for container in containers:
            if isinstance(container, dict):
                image = container.get("image")
                if image and isinstance(image, str):
                    image_names.append(image)

    return image_names


# needs to be at the bottom to add the defined functions
SUPPORTED_K8S_IMAGE_RESOURCE_TYPES: "dict[str, _ExtractImagesCallableAlias]" = {
    "CronJob": extract_images_from_cron_job,
    "Deployment": extract_images_from_template,
    "DeploymentConfig": extract_images_from_template,
    "DaemonSet": extract_images_from_template,
    "Job": extract_images_from_template,
    "Pod": extract_images_from_pod,
    "PodTemplate": extract_images_from_pod_template,
    "ReplicaSet": extract_images_from_template,
    "ReplicationController": extract_images_from_template,
    "StatefulSet": extract_images_from_template,
}
