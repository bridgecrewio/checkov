from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceAlwaysOn(BaseResourceValueCheck):
    def __init__(self) -> None:
        # "Azure App Service apps are automatically unloaded when there's no traffic. Unloading apps reduces resource
        # consumption when apps share a single App Services Plan.
        # After an app have been unloaded, the next web request will trigger a cold start of the app.
        # A cold start of the app can cause a noticeable performance issues and request timeouts.
        # Continuous WebJobs or WebJobs triggered with a CRON expression must use always on to start.
        # The Always On feature is implemented by the App Service load balancer,
        # periodically sending requests to the application root."
        name = "Ensure App Service is set to be always on"
        id = "CKV_AZURE_214"
        supported_resources = ('azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return 'site_config/[0]/always_on/[0]'


check = AppServiceAlwaysOn()
