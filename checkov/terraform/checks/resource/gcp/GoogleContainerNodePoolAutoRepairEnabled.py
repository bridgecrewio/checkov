from checkov.terraform.checks.resource.base_check import BaseResourceCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories


class GoogleContainerNodePoolAutoRepairEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure 'Automatic node repair' is enabled for Kubernetes Clusters"
        id = "CKV_GCP_9"
        supported_resources = ['google_container_node_pool']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for node auto-repair configuration on google_container_node_pool:
            https://www.terraform.io/docs/providers/google/r/container_node_pool.html
        :param conf: google_container_node_pool configuration
        :return: <CheckResult>
        """
        if 'management' in conf and 'auto_repair' in conf['management'][0]:
            if conf['management'][0]['auto_repair'][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleContainerNodePoolAutoRepairEnabled()
