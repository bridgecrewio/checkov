from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEHasLabels(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Kubernetes Clusters are configured with Labels"
        id = "CKV_GCP_21"
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
        if conf.get('resource_labels') and len(conf.get('resource_labels')[0].keys()) > 0:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GKEHasLabels()
