from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from typing import Dict, Any, List


class APIManagementCertsEnforced(BaseResourceCheck):
    def __init__(self) -> None:
        name: str = "Ensure Client Certificates are enforced for API management"
        id: str = "CKV_AZURE_152"
        supported_resources: tuple = ('Microsoft.ApiManagement/service',)
        categories: List[CheckCategories] = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
        self.evaluated_keys: List[str] = []

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if 'enableClientCertificate' in conf['properties']:
            client_certificate_enabled = conf['properties']['enableClientCertificate']
            if client_certificate_enabled is True:
                return CheckResult.PASSED
            self.evaluated_keys = ['/resources/properties/enableClientCertificate/']
            if client_certificate_enabled is False:
                return CheckResult.FAILED
        return CheckResult.FAILED


check = APIManagementCertsEnforced()
