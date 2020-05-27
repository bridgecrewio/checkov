from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GKEPodSecurityPolicyEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure PodSecurityPolicy controller is enabled on the Kubernetes Engine Clusters"
        id = "CKV_GCP_24"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "pod_security_policy_config/[0]/enabled"


check = GKEPodSecurityPolicyEnabled()
