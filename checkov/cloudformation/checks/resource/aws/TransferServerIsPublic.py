from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class TransferServerIsPublic(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Transfer Server is not exposed publicly."
        id = "CKV_AWS_164"
        supported_resources = ['AWS::Transfer::Server']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/EndpointType'

    def get_expected_values(self):
        return ["VPC", "VPC_ENDPOINT"]


check = TransferServerIsPublic()
