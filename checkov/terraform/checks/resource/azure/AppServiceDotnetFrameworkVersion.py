from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class AppServiceDotnetFrameworkVersion(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Net Framework' version is the latest, if used as a part of the web app"
        id = "CKV_AZURE_80"
        supported_resources = ['azurerm_app_service', 'azurerm_windows_web_app']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        # Supported .NET versions (LTS and STS currently supported by Microsoft)
        # v6.0 is EOL as of November 2024
        # v8.0 is LTS (supported until November 2026)
        # v9.0 is STS (supported until November 2026)
        # v10.0 is the latest version
        supported_versions = {"v8.0", "v9.0", "v10.0"}

        if conf.get('site_config') and isinstance(conf.get('site_config'), list):
            site_config = conf.get('site_config')[0]
            if site_config.get('dotnet_framework_version') and isinstance(site_config.get('dotnet_framework_version'), list):
                version = site_config.get('dotnet_framework_version')[0]
                if version in supported_versions:
                    return CheckResult.PASSED
                self.evaluated_keys = ['site_config/[0]/dotnet_framework_version']
                return CheckResult.FAILED
            if site_config.get('application_stack') and isinstance(site_config.get('application_stack'), list):
                stack = site_config.get('application_stack')[0]
                if stack.get('dotnet_version') and isinstance(stack.get('dotnet_version'), list):
                    version = stack.get('dotnet_version')[0]
                    if version in supported_versions:
                        return CheckResult.PASSED
                    self.evaluated_keys = ['site_config/[0]/application_stack/[0]/dotnet_version']
                    return CheckResult.FAILED

        return CheckResult.UNKNOWN

    def get_expected_values(self) -> List[str]:
        return ["v8.0", "v9.0", "v10.0"]


check = AppServiceDotnetFrameworkVersion()
