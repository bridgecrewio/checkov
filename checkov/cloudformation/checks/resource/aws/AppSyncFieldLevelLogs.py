from typing import Any, List

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppSyncFieldLevelLogs(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure AppSync has Field-Level logs enabled"
        id = "CKV_AWS_194"
        supported_resources = ("AWS::AppSync::GraphQLApi",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/LogConfig/FieldLogLevel"

    def get_expected_values(self) -> List[Any]:
        return ["ALL", "ERROR"]


check = AppSyncFieldLevelLogs()
