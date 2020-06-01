from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class GoogleSubnetworkLoggingEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that VPC Flow Logs is enabled for every subnet in a VPC Network"
        id = "CKV_GCP_26"
        supported_resources = ['google_compute_subnetwork']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'log_config'

    def get_expected_values(self):
        return [ANY_VALUE]


check = GoogleSubnetworkLoggingEnabled()
