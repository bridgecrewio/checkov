from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class PostgreSQLServerHasPublicAccessDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that PostgreSQL server disables public network access"
        id = "CKV_AZURE_68"
        supported_resources = ('Microsoft.DBforPostgreSQL/servers',)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return 'properties/publicNetworkAccess'

    def get_expected_value(self) -> str:
        return "Disabled"


check = PostgreSQLServerHasPublicAccessDisabled()
