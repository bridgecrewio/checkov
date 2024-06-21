from typing import Any, List

from checkov.arm.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppServiceDisallowCORS(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure that CORS disallows every resource to access app services"
        id = "CKV_AZURE_57"
        supported_resources = ("Microsoft.Web/sites",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED
        )

    def get_inspected_key(self) -> str:
        return 'properties/siteConfig/cors/allowedOrigins'

    def get_forbidden_values(self) -> List[Any]:
        return ['*']


check = AppServiceDisallowCORS()
