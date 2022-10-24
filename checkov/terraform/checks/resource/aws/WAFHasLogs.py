from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class WAFHasLogs(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Logging is enabled for WAF  Web Access Control Lists"
        id = "CKV_AWS_176"
        supported_resources = ('aws_waf_web_acl', 'aws_wafregional_web_acl')
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'logging_configuration/[0]/log_destination'

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = WAFHasLogs()
