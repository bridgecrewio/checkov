from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class ActionTrailLogAllEvents(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Action Trail Logging for all events"
        id = "CKV_ALI_5"
        supported_resources = ("alicloud_actiontrail_trail",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.FAILED,
        )

    def get_inspected_key(self) -> str:
        return "event_rw"

    def get_expected_value(self) -> Any:
        return "All"


check = ActionTrailLogAllEvents()
