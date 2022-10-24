from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class AppSyncLogging(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure AppSync has Logging enabled"
        id = "CKV_AWS_193"
        supported_resources = ("AWS::AppSync::GraphQLApi",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/LogConfig/CloudWatchLogsRoleArn"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AppSyncLogging()
