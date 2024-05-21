from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class APIManagementCertsEnforced(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Client Certificates are enforced for API management"
        id = "CKV_AZURE_152"
        supported_resources = ('Microsoft.ApiManagement/service',)
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'enableClientCertificate' in conf['properties']:
            client_certificate_enabled = conf['properties']['enableClientCertificate']
            if client_certificate_enabled is True:
                return CheckResult.PASSED
            self.evaluated_keys = ['/resources/properties/enableClientCertificate/']
            if client_certificate_enabled is False:
                return CheckResult.FAILED
        return CheckResult.FAILED


check = APIManagementCertsEnforced()
