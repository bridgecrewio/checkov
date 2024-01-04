from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class GKEDontUseNodePools(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        """
        Node pools are better configured in the separate resource google_container_node_pool
        or to quote the provider docs:
        "It is recommended that node pools be created and managed as separate resources as in the example above.
        This allows node pools to be added and removed without recreating the cluster.
        Node pools defined directly in the google_container_cluster resource cannot be removed
        without re-creating the cluster."
        Recreating a cluster in Production would be unwise.
        """

        name = "GKE Don't Use NodePools in the Cluster configuration"
        id = "CKV_GCP_123"
        supported_resources = ['google_container_cluster',]
        categories = [CheckCategories.KUBERNETES,]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'node_pool'

    def get_forbidden_values(self) -> Any:
        return [ANY_VALUE]


check = GKEDontUseNodePools()
