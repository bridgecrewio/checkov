from __future__ import annotations
from typing import Any, Mapping, TYPE_CHECKING, Union

from checkov.kubernetes.image_referencer.base_provider import BaseKubernetesProvider
from checkov.common.images.graph.image_referencer_provider import _ExtractImagesCallableAlias
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes

if TYPE_CHECKING:
    from igraph import Graph
    from networkx import DiGraph


class BaseKustomizeProvider(BaseKubernetesProvider):
    def __init__(self, graph_connector: Union[Graph, DiGraph],
                 supported_resource_types: dict[str, _ExtractImagesCallableAlias] | Mapping[str, _ExtractImagesCallableAlias],
                 report_mutator_data: dict[str, dict[str, Any]]) -> None:
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=supported_resource_types,
        )
        self.report_mutator_data = report_mutator_data

    def _get_resource_path(self, resource: dict[str, Any]) -> str:
        k8s_path = resource.get(CustomAttributes.FILE_PATH, "")
        dir_path = self.report_mutator_data.get('kustomizeFileMappings', {}).get(k8s_path, "")
        file_metadata = self.report_mutator_data.get('kustomizeMetadata', {}).get(dir_path, {})
        return str(file_metadata.get('filePath', ""))
