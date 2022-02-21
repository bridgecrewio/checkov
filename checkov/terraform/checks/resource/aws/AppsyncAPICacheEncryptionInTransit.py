from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppsyncCacheEncryptionInTransit(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Appsync API Cache is encrypted in transit"
        id = "CKV_AWS_215"
        supported_resources = ["aws_appsync_api_cache"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "transit_encryption_enabled"


check = AppsyncCacheEncryptionInTransit()
