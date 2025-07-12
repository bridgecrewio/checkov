from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
import time


class AKSMaxSurge33Test(BaseResourceCheck):
    def __init__(self) -> None:
        name = (
            "Ensure Azure Kubernetes Cluster (AKS) doesn't have a MaxSurge superior to 33% if not equal to 'Default'."
        )
        id = "CKV_AZURE_244"
        supported_resources = ("azurerm_kubernetes_cluster", "azurerm_kubernetes_cluster_node_pool")
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        max_surge_int = 0
        if self.entity_type == "azurerm_kubernetes_cluster":
            self.evaluated_keys = "default_node_pool/[0]/upgrade_settings/[0]/max_surge"
            if "default_node_pool" in conf.keys() and isinstance(conf["default_node_pool"][0], dict):
                default_np = conf["default_node_pool"][0]
                if "upgrade_settings" in default_np.keys() and isinstance(default_np["upgrade_settings"][0], dict):
                    upgrade_settings = default_np["upgrade_settings"][0]
                    if "max_surge" in upgrade_settings.keys() and isinstance(upgrade_settings["max_surge"][0], str):
                        max_surge = upgrade_settings["max_surge"][0]
                        max_surge_int = int(max_surge.replace("%", ""))

        else:
            self.evaluated_keys = "upgrade_settings/[0]/max_surge"
            if "upgrade_settings" in conf.keys() and isinstance(conf["upgrade_settings"], dict):
                upgrade_settings = conf["upgrade_settings"][0]
                if "max_surge" in upgrade_settings and isinstance(upgrade_settings["max_surge"][0], str):
                    max_surge = upgrade_settings[0]["max_surge"]
                    max_surge_int = int(max_surge.replace("%", ""))

        if max_surge_int > 33:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = AKSMaxSurge33Test()
