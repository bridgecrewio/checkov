from checkov.terraform.checks.resource.base_check import BaseResourceCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories


class GoogleContainerNodePoolAutoUpgradeEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure 'Automatic node upgrade' is enabled for Kubernetes Clusters"
        id = "CKV_GCP_10"
        supported_resources = ['google_container_node_pool']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for node auto-upgrade configuration on google_container_node_pool:
            https://www.terraform.io/docs/providers/google/r/container_node_pool.html
        :param conf: google_container_node_pool configuration
        :return: <CheckResult>
        """
        if 'management' in conf and 'auto_upgrade' in conf['management'][0]:
            if conf['management'][0]['auto_upgrade'][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleContainerNodePoolAutoUpgradeEnabled()
