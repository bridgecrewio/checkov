from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class FunctionAppHttpVersionLatest(BaseResourceValueCheck):

    def __init__(self) -> None:
        name = "Ensure that 'HTTP Version' is the latest, if used to run the Function app"
        id = "CKV_AZURE_67"
        supported_resources = ("Microsoft.Web/sites/slots", "Microsoft.Web/sites",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/siteConfig/http20Enabled"


check = FunctionAppHttpVersionLatest()
