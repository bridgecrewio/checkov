from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppsyncCacheEncryptionAtRest(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure AppSync API Cache is encrypted at rest"
        id = "CKV_AWS_214"
        supported_resources = ["aws_appsync_api_cache"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "at_rest_encryption_enabled"


check = AppsyncCacheEncryptionAtRest()
