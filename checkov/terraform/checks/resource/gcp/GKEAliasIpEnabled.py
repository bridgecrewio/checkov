from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class GKEAliasIpEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Kubernetes Cluster is created with Alias IP ranges enabled"
        id = "CKV_GCP_23"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'ip_allocation_policy'

    def get_expected_values(self):
        return [ANY_VALUE]


check = GKEAliasIpEnabled()
