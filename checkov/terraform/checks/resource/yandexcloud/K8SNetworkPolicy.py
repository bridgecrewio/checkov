from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE

class K8SNetworkPolicy(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure network policy is assigned to Kubernetes cluster."
        id = "CKV_YC_16"
        supported_resources = ["yandex_kubernetes_cluster"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "network_policy_provider"

    def get_expected_value(self):
        return ANY_VALUE
    
check = K8SNetworkPolicy()