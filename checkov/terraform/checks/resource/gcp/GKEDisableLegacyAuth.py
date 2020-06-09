from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GKEDisabledLegacyAuth(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Legacy Authorization is set to Disabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_7"
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
        if 'enable_legacy_abac' in conf:
            if conf['enable_legacy_abac'][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = GKEDisabledLegacyAuth()
