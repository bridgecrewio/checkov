from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEAliasIpEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Kubernetes Cluster is created with Alias IP ranges enabled"
        id = "CKV_GCP_23"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_compute_ssl_policy configuration
        :return: <CheckResult>
        """
        if conf.get('ip_allocation_policy'):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GKEAliasIpEnabled()
