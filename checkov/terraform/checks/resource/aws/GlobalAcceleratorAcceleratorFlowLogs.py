from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GlobalAcceleratorAcceleratorFlowLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Global Accelerator accelerator has flow logs enabled"
        id = "CKV_AWS_75"
        supported_resources = ['aws_globalaccelerator_accelerator']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "attributes/[0]/flow_logs_enabled"


check = GlobalAcceleratorAcceleratorFlowLogs()
