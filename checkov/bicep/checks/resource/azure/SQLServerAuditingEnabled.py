from typing import Any

from checkov.bicep.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class SQLServerAuditingEnabled(BaseResourceValueCheck):
    # this should be a graph check, due to the possible connection between
    # Microsoft.Sql/servers -> Microsoft.Sql/servers/auditingSettings
    # Microsoft.Sql/servers -> Microsoft.Sql/servers/databases/auditingSettings

    def __init__(self) -> None:
        name = "Ensure that 'Auditing' is set to 'Enabled' for SQL servers"
        id = "CKV_AZURE_23"
        supported_resources = (
            "Microsoft.Sql/servers/auditingSettings",
            "Microsoft.Sql/servers/databases/auditingSettings",
        )
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/state"

    def get_expected_value(self) -> Any:
        return "Enabled"


check = SQLServerAuditingEnabled()
