from __future__ import annotations

from typing import Any

from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AzureBatchAccountEndpointAccessDefaultAction(BaseResourceCheck):

    DISABLED_PUBLIC_NETWORK_ACCESS = "disabled"
    FORBIDDEN_NETWORK_ACCESS_DEFAULT_ACTION = "allow"

    def __init__(self) -> None:
        name = "Ensure that if Azure Batch account public network access in case 'enabled' then its account access must be 'deny'"
        id = "CKV_AZURE_248"
        supported_resources = ("Microsoft.Batch/batchAccounts",)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    @staticmethod
    def _exists_and_lower_equal(actual_value: Any, expected_lowercase_value: str) -> bool:
        return actual_value and str(actual_value).lower() == expected_lowercase_value

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get('properties')
        if not properties or not isinstance(properties, dict):
            return CheckResult.FAILED

        public_network_access = properties.get('publicNetworkAccess')
        # public network access is disabled, no need to check for account access default action
        if self._exists_and_lower_equal(public_network_access, self.DISABLED_PUBLIC_NETWORK_ACCESS):
            return CheckResult.PASSED

        network_profile = properties.get('networkProfile')
        if not network_profile:
            return CheckResult.PASSED
        account_access = network_profile.get('accountAccess')
        if not account_access:
            return CheckResult.PASSED
        default_action = account_access.get('defaultAction')
        if not self._exists_and_lower_equal(default_action, self.FORBIDDEN_NETWORK_ACCESS_DEFAULT_ACTION):
            return CheckResult.PASSED

        self.evaluated_keys = ["properties/networkProfile/accountAccess/defaultAction"]
        return CheckResult.FAILED


check = AzureBatchAccountEndpointAccessDefaultAction()
