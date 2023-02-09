from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class GKEPodSecurityPolicyEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Kubernetes Cluster is created with Private cluster enabled"
        id = "CKV_GCP_25"
        supported_resources = ("google_container_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "private_cluster_config"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = GKEPodSecurityPolicyEnabled()
