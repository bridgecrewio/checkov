from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceEnvironmentZoneRedundant(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure App Service Environment is zone redundant"
        id = "CKV_AZURE_231"
        supported_resources = ("azurerm_app_service_environment_v3",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "zone_redundant"


check = AppServiceEnvironmentZoneRedundant()
