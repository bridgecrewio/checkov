from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AKSNetworkPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        # apiVersion 2017-08-03 = Fail - No networkProfile option to configure
        name = "Ensure AKS cluster has Network Policy configured"
        id = "CKV_AZURE_7"
        supported_resources = ('Microsoft.ContainerService/managedClusters',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "apiVersion" in conf:
            if conf["apiVersion"] == "2017-08-31":
                # No networkProfile option to configure
                return CheckResult.FAILED

        properties = conf.get('properties')
        if not properties or not isinstance(properties, dict):
            return CheckResult.FAILED
        network_profile = properties.get('networkProfile')
        if not network_profile:
            return CheckResult.FAILED
        network_policy = network_profile.get('networkPolicy')
        if network_policy:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = AKSNetworkPolicy()
