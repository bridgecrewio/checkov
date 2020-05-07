from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GKEMonitoringEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Stackdriver Monitoring is set to Enabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_8"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for monitoring configuration on google_container_cluster:
            https://www.terraform.io/docs/providers/google/r/container_cluster.html
        :param conf: google_container_cluster configuration
        :return: <CheckResult>
        """
        if 'monitoring_service' in conf:
            if conf['monitoring_service'][0] == "none":
                return CheckResult.FAILED
        return CheckResult.PASSED


check = GKEMonitoringEnabled()
