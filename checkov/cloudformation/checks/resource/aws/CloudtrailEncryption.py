from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class CloudtrailEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CloudTrail logs are encrypted at rest using KMS CMKs"
        id = "CKV_AWS_35"
        supported_resources = ['AWS::CloudTrail::Trail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/KMSKeyId'

    def get_expected_value(self):
        return ANY_VALUE

check = CloudtrailEncryption()
