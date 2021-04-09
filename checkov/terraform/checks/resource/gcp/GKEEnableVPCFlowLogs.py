from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

class GKEEnableVPCFlowLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Enable VPC Flow Logs and Intranode Visibility"
        id = "CKV_GCP_61"
        supported_resources = ['google_container_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'enable_intranode_visibility'

    def get_expected_values(self):
        return [True]


check = GKEEnableVPCFlowLogs()
