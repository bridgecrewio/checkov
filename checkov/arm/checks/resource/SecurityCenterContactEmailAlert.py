from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class SecurityCenterContactEmailAlert(BaseResourceCheck):
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.security/securitycontacts
        name = "Ensure that 'Send email notification for high severity alerts' is set to 'On'"
        id = "CKV_AZURE_21"
        supported_resources = ('Microsoft.Security/securityContacts',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "properties" in conf:
            if "alertNotifications" in conf["properties"]:
                if str(conf["properties"]["alertNotifications"]).lower() == "on":
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['properties', 'properties/alertNotifications']


check = SecurityCenterContactEmailAlert()
