from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GKESecureBootforShieldedNodes(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Secure Boot for Shielded GKE Nodes is Enabled"
        id = "CKV_GCP_68"
        supported_resources = ['google_container_cluster', 'google_container_node_pool']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'node_config' in conf.keys():
            node = conf["node_config"][0]
            if isinstance(node, dict) and 'shielded_instance_config' in node:
                monitor = node["shielded_instance_config"][0]
                if monitor["enable_secure_boot"] == [True]:
                    return CheckResult.PASSED
                else:
                    return CheckResult.FAILED
            else:
                # as default is true this is a pass
                return CheckResult.FAILED
        else:
            return CheckResult.UNKNOWN

    def get_inspected_key(self):
        return 'node_config/[0]/shielded_instance_config/[0]/enable_secure_boot'

    def get_expected_values(self):
        return [True]


check = GKESecureBootforShieldedNodes()
