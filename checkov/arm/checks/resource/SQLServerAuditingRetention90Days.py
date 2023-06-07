from typing import Dict, Any, List

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/databases/auditingsettings


class SQLServerAuditingRetention90Days(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Auditing' Retention is 'greater than 90 days' for SQL servers"
        id = "CKV_AZURE_24"
        supported_resources = ("Microsoft.Sql/servers",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf_20210501preview(self, conf: Dict[str, Any]) -> CheckResult:
        resources = []
        for r in conf.get('resources') or []:
            resources += r.get('resources') or []
        return self.scan_sub_resources(resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if conf.get('apiVersion') == '2021-05-01-preview':
            # The structure is different, example in test dir
            return self.scan_resource_conf_20210501preview(conf)
        self.evaluated_keys = ["resources"]
        resources = conf.get("resources") or []
        return self.scan_sub_resources(resources)

    def scan_sub_resources(self, resources: List[Dict[str, Any]]) -> CheckResult:
        for idx, resource in enumerate(resources):
            self.evaluated_keys = [
                f"resources/[{idx}]/type",
                f"resources/[{idx}]/properties/state",
                f"resources/[{idx}]/properties/retentionDays",
            ]
            if resource.get("type") in (
                    "Microsoft.Sql/servers/databases/auditingPolicies",
                    "Microsoft.Sql/servers/databases/auditingSettings",
                    "auditingSettings",
            ):
                properties = resource.get("properties")
                if isinstance(properties, dict):
                    state = properties.get("state")
                    if isinstance(state, str) and state.lower() == "enabled":
                        retention = properties.get("retentionDays")
                        if isinstance(retention, int) and retention >= 90:
                            return CheckResult.PASSED

        return CheckResult.FAILED


check = SQLServerAuditingRetention90Days()
