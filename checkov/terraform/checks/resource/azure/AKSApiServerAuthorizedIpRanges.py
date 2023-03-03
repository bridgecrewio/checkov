from __future__ import annotations

from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSApiServerAuthorizedIpRanges(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure AKS has an API Server Authorized IP Ranges enabled"
        id = "CKV_AZURE_6"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "api_server_authorized_ip_ranges/[0]"

    def get_expected_value(self) -> Any:
        return ANY_VALUE

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # can't be set for private cluster
        private_cluster_enabled = conf.get("private_cluster_enabled", [False])[0]
        if private_cluster_enabled:
            return CheckResult.PASSED
        return super().scan_resource_conf(conf)


check = AKSApiServerAuthorizedIpRanges()
