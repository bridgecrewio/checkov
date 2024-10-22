from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class SpannerDatabaseDeletionProtection(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Spanner Database has deletion protection enabled"
        id = "CKV_GCP_119"
        supported_resources = ['google_spanner_database']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return 'deletion_protection'

    def get_expected_value(self) -> bool:
        return True


check = SpannerDatabaseDeletionProtection()
