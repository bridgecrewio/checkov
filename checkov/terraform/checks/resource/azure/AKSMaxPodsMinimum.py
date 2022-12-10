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
        if "max_pods" in conf.keys() and isinstance(conf["max_pods"][0], int):
            max_pods = conf["max_pods"][0]

        if "default_node_pool" in conf.keys():
            self.evaluated_keys = ["default_node_pool/max_pods"]
            pool = conf["default_node_pool"][0]
            if "max_pods" in pool.keys():
                max_pods_list = pool["max_pods"]
                if max_pods_list and isinstance(max_pods_list, list) and isinstance(max_pods_list[0], int):
                    max_pods = max_pods_list[0]

        if max_pods < 50:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = AKSMaxPodsMinimum()
