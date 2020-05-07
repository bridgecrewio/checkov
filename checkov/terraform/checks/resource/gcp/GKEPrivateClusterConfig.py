from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEPodSecurityPolicyEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Kubernetes Cluster is created with Private cluster enabled"
        id = "CKV_GCP_25"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('private_cluster_config'):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GKEPodSecurityPolicyEnabled()
