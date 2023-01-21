from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSMaxPodsMinimum(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Kubernetes Cluster (AKS) nodes should use a minimum number of 50 pods."
        id = "CKV_AZURE_168"
        supported_resources = ("azurerm_kubernetes_cluster", "azurerm_kubernetes_cluster_node_pool")
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        max_pods = 30  # default is 30

        self.evaluated_keys = ["max_pods"]
        pods = conf.get("max_pods")
        if pods and isinstance(pods, list):
            pods = pods[0]
            if self._is_variable_dependant(pods):
                return CheckResult.UNKNOWN
            elif isinstance(pods, int):
                max_pods = pods

        pool = conf.get("default_node_pool")
        if pool and isinstance(pool, list):
            self.evaluated_keys = ["default_node_pool/max_pods"]

            pool = pool[0]
            pods = pool.get("max_pods")
            if pods and isinstance(pods, list):
                pods = pods[0]
                if self._is_variable_dependant(pods):
                    return CheckResult.UNKNOWN
                elif isinstance(pods, int):
                    max_pods = pods

        if max_pods < 50:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = AKSMaxPodsMinimum()
