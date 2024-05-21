from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class APIManagementCertsEnforced(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Client Certificates are enforced for API management"
        id = "CKV_AZURE_152"
        supported_resources = ('Microsoft.ApiManagement/service',)
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        resources = conf
        for resource in resources:
            if 'type' in resource:
                if resources['type'] == 'Microsoft.ApiManagement/service':
                    sku_name = resources['properties']['sku']['name']
                    if sku_name == "Consumption":
                        name = resources['name']
                        if 'clientCertificateEnabled' in resources['properties']:
                            client_certificate_enabled = resources['properties']['clientCertificateEnabled']
                            if client_certificate_enabled is True:
                                return CheckResult.PASSED
                            self.evaluated_keys = ['/resources/properties/clientCertificateEnabled/']
                            if client_certificate_enabled is False:
                                return CheckResult.FAILED
        return CheckResult.FAILED


check = APIManagementCertsEnforced()
