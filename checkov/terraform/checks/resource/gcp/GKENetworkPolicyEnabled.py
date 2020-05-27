from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GKENetworkPolicyEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Network Policy is enabled on Kubernetes Engine Clusters"
        id = "CKV_GCP_12"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
            Looks for monitoring configuration on google_container_cluster:
            https://www.terraform.io/docs/providers/google/r/container_cluster.html
        :param conf: google_container_cluster configuration
        :return: <CheckResult>
        """

        return 'network_policy/[0]/enabled'


check = GKENetworkPolicyEnabled()
