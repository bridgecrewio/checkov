from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck

class AthenaWorkgroupConfiguration(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Athena Workgroup should enforce configuration to prevent client disabling encryption"
        id = "CKV_AWS_82"
        supported_resources = ['AWS::Athena::WorkGroup']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/WorkGroupConfiguration/EnforceWorkGroupConfiguration'


check = AthenaWorkgroupConfiguration()
