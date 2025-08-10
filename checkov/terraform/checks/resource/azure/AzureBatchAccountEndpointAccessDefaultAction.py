from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AzureBatchAccountEndpointAccessDefaultAction(BaseResourceCheck):

    def __init__(self) -> None:
        name = "Ensure that if Azure Batch account public network access in case 'enabled' then its account access must be 'deny'"
        id = "CKV_AZURE_248"
        supported_resources = ("azurerm_batch_account",)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:

        public_network_access = conf.get('public_network_access_enabled', [None])[0]
        # public network access is disabled, no need to check for account access default action
        if public_network_access is False:
            return CheckResult.PASSED

        network_profile: dict[str, Any] | None = conf.get('network_profile', [None])[0]
        if not network_profile:
            return CheckResult.PASSED
        account_access: dict[str, Any] | None = network_profile.get('account_access', [None])[0]
        if not account_access:
            return CheckResult.PASSED
        default_action: str | None = account_access.get('default_action', [None])[0]
        if not default_action or str(default_action).lower() != "allow":
            return CheckResult.PASSED

        self.evaluated_keys = ["network_profile/[0]/account_access/[0]/default_action"]
        return CheckResult.FAILED


check = AzureBatchAccountEndpointAccessDefaultAction()
