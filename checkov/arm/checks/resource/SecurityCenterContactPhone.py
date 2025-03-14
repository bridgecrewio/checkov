from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class SecurityCenterContactPhone(BaseResourceCheck):
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.security/securitycontacts
        name = "Ensure that security contact 'Phone number' is set"
        id = "CKV_AZURE_20"
        supported_resources = ('Microsoft.Security/securityContacts',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "properties" in conf:
            if "phone" in conf["properties"]:
                if conf["properties"]["phone"]:
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties", "properties/phone"]


check = SecurityCenterContactPhone()
