from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class MSKClusterNodesArePrivate(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure MSK nodes are private"
        id = "CKV_AWS_291"
        supported_resources = ['aws_msk_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "broker_node_group_info/[0]/connectivity_info/[0]/public_access/[0]/type"

    def get_forbidden_values(self):
        return ["SERVICE_PROVIDED_EIPS"]


check = MSKClusterNodesArePrivate()
