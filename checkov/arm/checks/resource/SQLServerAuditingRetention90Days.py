from typing import Dict, Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list

# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/databases/auditingsettings


class SQLServerAuditingRetention90Days(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Auditing' Retention is 'greater than 90 days' for SQL servers"
        id = "CKV_AZURE_24"
        supported_resources = ("Microsoft.Sql/servers",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["resources"]
        resources = conf.get("resources") or []
        for idx, resource in enumerate(force_list(resources)):
            self.evaluated_keys = [
                f"resources/[{idx}]/type",
                f"resources/[{idx}]/properties/state",
                f"resources/[{idx}]/properties/retentionDays",
            ]
            if resource.get("type") in (
                "Microsoft.Sql/servers/databases/auditingSettings",
                'Microsoft.Sql/servers/auditingSettings',
                "auditingSettings",
            ):
                return self.check_resource(resource)
            elif resource.get("type") in (
                "databases"
            ):
                sub_resources = resource.get("resources") or []
                for sr in sub_resources:
                    if sr.get("type") == "Microsoft.Sql/servers/databases/auditingPolicies":
                        return self.check_resource(sr)

        return CheckResult.FAILED

    @staticmethod
    def check_resource(resource: Dict[str, Any]) -> CheckResult:
        properties = resource.get("properties")
        if isinstance(properties, dict):
            state = properties.get("state")
            if isinstance(state, str) and state.lower() == "enabled":
                retention = properties.get("retentionDays")
                if isinstance(retention, int) and retention >= 90:
                    return CheckResult.PASSED
                if isinstance(retention, str):
                    try:
                        if int(retention) >= 90:
                            return CheckResult.PASSED
                    except ValueError:  # not a valid number
                        return CheckResult.FAILED
        return CheckResult.FAILED


check = SQLServerAuditingRetention90Days()
