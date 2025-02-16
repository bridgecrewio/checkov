from __future__ import annotations

from typing import Dict, List

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppServiceInstanceMinimum(BaseResourceCheck):
    def __init__(self) -> None:
        # "App Services Plans provides a configurable number of instances that will run apps.
        # When a single instance is configured your app may be temporarily unavailable during unplanned interruptions.
        # In most circumstances, Azure will self-heal faulty app service instances automatically.
        # How-ever during this time there may interruptions to your workload."
        name = "Ensure App Service has a minimum number of instances for failover"
        id = "CKV_AZURE_212"
        supported_resources = ("Microsoft.Web/sites", "Microsoft.Web/sites/slots")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Dict[str, Dict[str, int]]]) -> CheckResult:
        if "properties" in conf:
            if conf.get("properties", {}).get("siteConfig") is not None:
                if "numberOfWorkers" in conf["properties"]["siteConfig"]:
                    worker_count = conf["properties"]["siteConfig"]["numberOfWorkers"]
                    if worker_count:
                        if not isinstance(worker_count, int):
                            return CheckResult.UNKNOWN
                        if worker_count > 1:
                            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties", "properties/siteConfig", "properties/siteConfig/numberOfWorkers"]


check = AppServiceInstanceMinimum()
