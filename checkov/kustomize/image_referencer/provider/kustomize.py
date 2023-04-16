from typing import Any, Union, Dict

import networkx
import igraph

from checkov.kubernetes.image_referencer.provider.k8s import SUPPORTED_K8S_IMAGE_RESOURCE_TYPES
from checkov.kustomize.image_referencer.base_provider import BaseKustomizeProvider


class KustomizeProvider(BaseKustomizeProvider):
    def __init__(self, graph_connector: Union[igraph.Graph, networkx.DiGraph], report_mutator_data: Dict[str, Dict[str, Any]]):
        super().__init__(
            graph_connector=graph_connector,
            supported_resource_types=SUPPORTED_K8S_IMAGE_RESOURCE_TYPES,
            report_mutator_data=report_mutator_data
        )
