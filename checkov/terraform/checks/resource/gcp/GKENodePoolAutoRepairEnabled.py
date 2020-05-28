from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GKENodePoolAutoRepairEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure 'Automatic node repair' is enabled for Kubernetes Clusters"
        id = "CKV_GCP_9"
        supported_resources = ['google_container_node_pool']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
            Looks for node auto-repair configuration on google_container_node_pool:
            https://www.terraform.io/docs/providers/google/r/container_node_pool.html
        :param conf: google_container_node_pool configuration
        :return: <CheckResult>
        """

        return 'management/[0]/auto_repair/[0]'


check = GKENodePoolAutoRepairEnabled()
