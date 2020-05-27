from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEClusterLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Stackdriver Logging is set to Enabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_1"
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
        if 'logging_service' in conf.keys():
            if conf['logging_service'][0] == "none":
                return CheckResult.FAILED
        return CheckResult.PASSED


check = GKEClusterLogging()
