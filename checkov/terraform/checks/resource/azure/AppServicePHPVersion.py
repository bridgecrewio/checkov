from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AppServicePHPVersion(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'PHP version' is the latest, if used to run the web app"
        id = "CKV_AZURE_81"
        supported_resources = ['azurerm_app_service']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if len(conf.get('site_config', [])) > 0 and 'php_version' in conf['site_config'][0]:
            if conf['site_config'][0]['php_version'][0] != '7.4':
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AppServicePHPVersion()
