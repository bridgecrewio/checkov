from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AppServiceAuthentication(BaseResourceCheck):
    def __init__(self):
        name = "Ensure App Service Authentication is set on Azure App Service"
        id = "CKV_AZURE_13"
        supported_resources = ('azurerm_app_service', 'azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'auth_settings/[0]/enabled/[0]'

    def scan_resource_conf(self, conf):
        if conf.get('auth_settings') and isinstance(conf.get('auth_settings'), list):
            auth = conf.get('auth_settings')[0]
            if auth.get("enabled") and isinstance(auth.get("enabled"), list):
                enabled = auth.get("enabled")[0]
                if enabled:
                    return CheckResult.PASSED
                return CheckResult.FAILED
        if conf.get('auth_settings_v2') and isinstance(conf.get('auth_settings_v2'), list):
            auth = conf.get('auth_settings_v2')[0]
            if auth.get("auth_enabled") and isinstance(auth.get("auth_enabled"), list):
                enabled = auth.get("auth_enabled")[0]
                if enabled:
                    return CheckResult.PASSED
                return CheckResult.FAILED
        return CheckResult.FAILED


check = AppServiceAuthentication()
