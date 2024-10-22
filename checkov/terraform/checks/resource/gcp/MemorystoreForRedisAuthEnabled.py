from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class MemorystoreForRedisAuthEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Memorystore for Redis has AUTH enabled"
        id = "CKV_GCP_95"
        supported_resources = ("google_redis_instance",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "auth_enabled"

    # Accounts for if key is present but is set to False
    def get_expected_value(self) -> Any:
        return True


check = MemorystoreForRedisAuthEnabled()
