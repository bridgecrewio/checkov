from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class RedisCacheEnableNonSSLPort(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that only SSL are enabled for Cache for Redis"
        id = "CKV_AZURE_91"
        supported_resources = ("Microsoft.Cache/Redis",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "properties/enableNonSSLPort"

    def get_expected_value(self) -> bool:
        return False


check = RedisCacheEnableNonSSLPort()
