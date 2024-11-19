from __future__ import annotations

from typing import Any, Dict, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AKSUpgradeChannel(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure AKS cluster upgrade channel is chosen"
        id = "CKV_AZURE_171"
        supported_resources = ("azurerm_kubernetes_cluster",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if 'automatic_channel_upgrade' in conf:
            automatic_channel_upgrade = conf.get('automatic_channel_upgrade')
            if isinstance(automatic_channel_upgrade, list) and automatic_channel_upgrade != ['none']:
                return CheckResult.PASSED

        if 'automatic_upgrade_channel' in conf:
            automatic_upgrade_channel = conf.get('automatic_upgrade_channel')
            if isinstance(automatic_upgrade_channel, list) and automatic_upgrade_channel != ['none']:
                return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['automatic_upgrade_channel', 'automatic_channel_upgrade']


check = AKSUpgradeChannel()
