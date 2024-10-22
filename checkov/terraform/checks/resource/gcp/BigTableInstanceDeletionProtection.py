from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class BigTableInstanceDeletionProtection(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Big Table Instances have deletion protection enabled"
        id = "CKV_GCP_122"
        supported_resources = ['google_bigtable_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return 'deletion_protection'

    def get_expected_value(self):
        return True


check = BigTableInstanceDeletionProtection()
