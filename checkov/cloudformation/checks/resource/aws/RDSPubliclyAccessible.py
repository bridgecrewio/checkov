from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class RDSPubliclyAccessible(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure all data stored in the RDS bucket is not public accessible"
        id = "CKV_AWS_17"
        supported_resources = ['AWS::RDS::DBInstance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_expected_value(self):
        return False

    def get_inspected_key(self):
        return 'Properties/PubliclyAccessible'


check = RDSPubliclyAccessible()
