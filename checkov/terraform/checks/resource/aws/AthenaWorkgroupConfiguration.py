from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AthenaWorkgroupConfiguration(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Athena Workgroup should enforce configuration to prevent client disabling encryption"
        id = "CKV_AWS_82"
        supported_resources = ['aws_athena_workgroup']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "configuration/[0]/enforce_workgroup_configuration"


check = AthenaWorkgroupConfiguration()
