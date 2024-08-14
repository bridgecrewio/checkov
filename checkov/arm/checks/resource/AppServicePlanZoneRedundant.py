from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AppServicePlanZoneRedundant(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        To enhance the resiliency and reliability of business-critical workloads,
        it's recommended to deploy new App Service Plans with zone-redundancy.

        There's no additional cost associated with enabling availability zones.
        Pricing for a zone redundant App Service is the same as a single zone App Service.
        """
        name = "Ensure the App Service Plan is zone redundant"
        id = "CKV_AZURE_225"
        supported_resources = ["Microsoft.Web/serverfarms", ]
        categories = [CheckCategories.BACKUP_AND_RECOVERY, ]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "properties/zoneRedundant"

    def get_expected_value(self) -> bool:
        return True


check = AppServicePlanZoneRedundant()
