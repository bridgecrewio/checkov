from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleComputeExternalIP(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that Compute instances do not have public IP addresses"
        id = "CKV_GCP_40"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'access_config'

    def get_forbidden_values(self):
        return [ANY_VALUE]


check = GoogleComputeExternalIP()
