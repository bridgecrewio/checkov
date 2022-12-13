from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AppServiceInstanceMinimum(BaseResourceCheck):
    def __init__(self):
        # "App Services Plans provides a configurable number of instances that will run apps.
        # When a single instance is configured your app may be temporarily unavailable during unplanned interruptions.
        # In most circumstances, Azure will self-heal faulty app service instances automatically.
        # How-ever during this time there may interruptions to your workload."
        name = "Ensure App Service plan suitable for production use"
        id = "CKV_AZURE_212"
        supported_resources = ['azurerm_service_plan']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("worker_count"):
            if conf.get("worker_count")[0] > 1:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = AppServiceInstanceMinimum()
