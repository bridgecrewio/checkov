from typing import List, Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class FunctionAppDisallowCORS(BaseResourceNegativeValueCheck):

    def __init__(self) -> None:
        name = "Ensure function apps are not accessible from all regions"
        id = "CKV_AZURE_62"
        supported_resources = ("Microsoft.Web/sites",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "properties/siteConfig/cors/allowedOrigins"

    def get_forbidden_values(self) -> List[Any]:
        return ["*"]


check = FunctionAppDisallowCORS()
