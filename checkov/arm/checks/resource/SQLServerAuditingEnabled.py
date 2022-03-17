from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/databases/auditingsettings


class SQLServerAuditingEnabled(BaseResourceCheck):
    # this should be a graph check, due to the possible connection between
    # Microsoft.Sql/servers -> Microsoft.Sql/servers/auditingSettings
    # Microsoft.Sql/servers -> Microsoft.Sql/servers/databases/auditingSettings

    def __init__(self) -> None:
        name = "Ensure that 'Auditing' is set to 'Enabled' for SQL servers"
        id = "CKV_AZURE_23"
        supported_resources = ("Microsoft.Sql/servers", "Microsoft.Sql/servers/databases")
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        resources = conf.get("resources")
        if resources and isinstance(resources, list):
            for resource in resources:
                if resource.get("type") in (
                    "auditingSettings",
                    "Microsoft.Sql/servers/auditingSettings",
                    "Microsoft.Sql/servers/databases/auditingSettings",
                ):
                    properties = resource.get("properties")
                    if properties:
                        state = properties.get("state")
                        if state and state.lower() == "enabled":
                            return CheckResult.PASSED

        return CheckResult.FAILED


check = SQLServerAuditingEnabled()
