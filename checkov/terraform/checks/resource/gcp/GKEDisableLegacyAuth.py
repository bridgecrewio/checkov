from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class GKEDisabledLegacyAuth(BaseResourceNegativeValueCheck):
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
        inspected_key = self.get_inspected_key()
        if inspected_key in conf:
            if conf[inspected_key][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED

    def get_inspected_key(self):
        return 'enable_legacy_abac'

    def get_vulnerable_values(self):
        return [True]


check = GKEDisabledLegacyAuth()
