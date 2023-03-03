from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AppServiceClientCertificate(BaseResourceCheck):
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.web/2019-08-01/sites
        # clientCertEnabled default = false
        name = "Ensure the web app has 'Client Certificates (Incoming client certificates)' set"
        id = "CKV_AZURE_17"
        supported_resources = ('Microsoft.Web/sites',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "properties" in conf:
            if "clientCertEnabled" in conf["properties"]:
                if str(conf["properties"]["clientCertEnabled"]).lower() == "true":
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = AppServiceClientCertificate()
