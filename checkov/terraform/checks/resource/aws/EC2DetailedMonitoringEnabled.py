from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class EC2DetailedMonitoringEnabled(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that detailed monitoring is enabled for EC2 instances"
        id = "CKV_AWS_126"
        supported_resources = ['aws_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'monitoring'

    def get_expected_value(self):
        return True


check = EC2DetailedMonitoringEnabled()
