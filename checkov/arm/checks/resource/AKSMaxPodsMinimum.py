from __future__ import annotations
from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from typing import Optional


class AKSMaxPodsMinimum(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Kubernetes Cluster (AKS) nodes should use a minimum number of 50 pods."
        id = "CKV_AZURE_168"
        supported_resources = ("Microsoft.ContainerService/managedClusters",
                               "Microsoft.ContainerService/managedClusters/agentPools", )
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        max_pods: Optional[int] = 30

        properties = conf.get("properties")
        if properties and isinstance(properties, dict):
            max_pods = properties.get("maxPods")

        if "agentPoolProfiles" in properties:
            if "maxPods" in properties["agentPoolProfiles"][0]:
                max_pods = properties["agentPoolProfiles"][0]["maxPods"]

        if max_pods is None or max_pods < 50:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = AKSMaxPodsMinimum()
