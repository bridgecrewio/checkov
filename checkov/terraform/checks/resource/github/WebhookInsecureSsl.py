from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck

class WebhookInsecureSsl(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Repository Webhook uses secure Ssl"
        id = "CKV_GIT_2"
        supported_resources = ["github_repository_webhook"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "configuration/[0]/insecure_ssl/[0]"

    def get_expected_value(self):
        return False


check = WebhookInsecureSsl()
