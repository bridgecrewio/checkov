from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AppServiceMinTLSVersion(BaseResourceCheck):
    def __init__(self):
        name = "Ensure web app is using the latest version of TLS encryption"
        id = "CKV_AZURE_15"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'site_config' in conf and 'min_tls_version' in conf['site_config'][0]:
            if conf['site_config'][0]['min_tls_version'][0] != '1.2':
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AppServiceMinTLSVersion()
