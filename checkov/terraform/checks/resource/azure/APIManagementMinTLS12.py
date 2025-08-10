from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class APIManagementMinTLS12(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure API management uses at least TLS 1.2"
        id = "CKV_AZURE_173"
        supported_resources = ("azurerm_api_management",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get('security'):
            security = conf['security'][0]
            if 'enable_back_end_ssl30' in security:
                if security['enable_back_end_ssl30'][0]:
                    self.evaluated_keys = ['security/[0]/enable_back_end_ssl30']
                    return CheckResult.FAILED
            if 'enable_backend_tls10' in security:
                if security['enable_backend_tls10'][0]:
                    self.evaluated_keys = ['security/[0]/enable_backend_tls10']
                    return CheckResult.FAILED
            if 'enable_frontend_ssl30' in security:
                if security['enable_frontend_ssl30'][0]:
                    self.evaluated_keys = ['security/[0]/enable_frontend_ssl30']
                    return CheckResult.FAILED
            if 'enable_frontend_tls10' in security:
                if security['enable_frontend_tls10'][0]:
                    self.evaluated_keys = ['security/[0]/enable_frontend_tls10']
                    return CheckResult.FAILED
            if 'enable_frontend_tls11' in security:
                if security['enable_frontend_tls11'][0]:
                    self.evaluated_keys = ['security/[0]/enable_frontend_tls11']
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = APIManagementMinTLS12()
