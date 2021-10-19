from checkov.cloudformation.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class RDSPubliclyAccessible(BaseResourceNegativeValueCheck):

    def __init__(self):
        name = "Ensure all data stored in RDS is not publicly accessible"
        id = "CKV_AWS_17"
        supported_resources = ['AWS::RDS::DBInstance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_forbidden_values(self):
        return [True]

    def get_inspected_key(self):
        return 'Properties/PubliclyAccessible'


check = RDSPubliclyAccessible()
