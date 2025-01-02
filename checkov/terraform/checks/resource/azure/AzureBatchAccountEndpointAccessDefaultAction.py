from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AzureBatchAccountEndpointAccessDefaultAction(BaseResourceCheck):

    def __init__(self) -> None:
        name = "Ensure that Azure Batch account public network access is 'enabled' account access default action is 'ignore'"
        id = "CKV_AZURE_244"
        supported_resources = ("azurerm_batch_account",)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:

        # public network access is disabled, no need to check for account access default action
        public_network_access = conf.get('public_network_access_enabled', [None])[0]
        if not public_network_access:
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

        return CheckResult.FAILED


check = AzureBatchAccountEndpointAccessDefaultAction()
