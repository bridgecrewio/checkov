from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleComputeSerialPorts(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure 'Enable connecting to serial ports' is not enabled for VM Instance"
        id = "CKV_GCP_35"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'metadata/[0]/serial-port-enable'

    def get_forbidden_values(self):
        return [True]


check = GoogleComputeSerialPorts()
